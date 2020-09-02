import graphene
from graphene_django.types import DjangoObjectType, ObjectType
from graphene_django.filter import DjangoFilterConnectionField

# from django.db.models.expressions import RawSQL
from django.db import connection

from time import time
import pandas as pd

import baseline.models as bl
# import baseline.models_virtual as bl_v
import ge.models as ge
import project.models as pjt
import project.schema as pjt_sch
import libs.timeline.primitive_estimation as lib


# TODO check to be added if the output is unique and protection against looped queries

# def retrieve_data_from_db():
#     return pjt.Project.objects.all()



class ProjectTimeline(DjangoObjectType):
    class Meta:
        model = bl.Project
        exclude = ('baseline', 'id',)

    raw_sql_dependency = '''
        select 
            array_agg(predecessor_id)
        from baseline_projectdependency
        where
            llp = '{llp}'
        and
            baseline_id = {baseline_id}
        and
            project_id = {project_id}
        group by project_id
    '''

    worktime_planned = graphene.String()
    predecessors_ID_F_S = graphene.List(graphene.Int) # TODO add support for other types and create graphene object for filtering
    L_L_P_predecessors_ID_F_S = graphene.List(graphene.Int)
    start = graphene.String()
    finish = graphene.String()

    def resolve_start(self, info):
        return self.start.strftime('%Y-%m-%d')
    def resolve_finish(self, info):
        return self.finish.strftime('%Y-%m-%d')

    def resolve_predecessors_ID_F_S(self, info):
        cur = connection.cursor()
        cur.execute(ProjectTimeline.raw_sql_dependency.format(llp=False, baseline_id=self.baseline.pk, project_id=self.project.pk))
        result = cur.fetchall()
        if len(result) > 1:
            raise Exception("ERROR: Cannot return more than one lines")
        return [] if len(result) == 0 else result[0][0]

    def resolve_L_L_P_predecessors_ID_F_S(self, info):
        cur = connection.cursor()
        cur.execute(ProjectTimeline.raw_sql_dependency.format(llp=True, baseline_id=self.baseline.pk, project_id=self.project.pk))
        result = cur.fetchall()
        if len(result) > 1:
            raise Exception("ERROR: Cannot return more than one lines")
        return [] if len(result) == 0 else result[0][0]



class Timeline(DjangoObjectType):
    class Meta:
        model = bl.Timeline
        exclude = ('baseline', 'id',)


class ProjectDependency(DjangoObjectType):
    class Meta:
        model = bl.ProjectDependency
        exclude = ('baseline', 'id',)


class Baseline(DjangoObjectType):
    class Meta:
        model = bl.Baseline
        fields = '__all__'
    id = graphene.Int(required=True)
    
    belongs_to = graphene.Field(pjt_sch.Project)
    timeline = graphene.List(Timeline)
    dependencies = graphene.List(ProjectDependency)
    projects = graphene.List(ProjectTimeline)
    L_L_P_projects = graphene.List(ProjectTimeline)

    def resolve_belongs_to(self, info):
        if len(ge.Edge.objects.filter(source_vertex=self.pk, edge_type_id=ge.EdgeType.objects.get(id='belongs_to'))) == 0:
            return None
        return pjt.Project.objects.get(pk=ge.Edge.objects.filter(source_vertex=self.pk, edge_type_id=ge.EdgeType.objects.get(id='belongs_to'))[0].target_vertex.pk)

    def resolve_timeline(self, info):
        return bl.Timeline.objects.filter(baseline=self.id)

    def resolve_dependencies(self, info):
        return bl.ProjectDependency.objects.filter(baseline=self.id)

    def resolve_projects(self, info):
        return bl.Project.objects.filter(baseline=self.id)

    def resolve_L_L_P_projects(self, info):
        return bl.Project.objects.filter(baseline=self.id, llp=True)




class Query(ObjectType):
    baseline = graphene.Field(Baseline, id=graphene.Int())

    def resolve_baseline(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return bl.Baseline.objects.get(pk=id)
        return None





class BaselineCreator(graphene.Mutation):
    class Arguments:
        project = graphene.Int(required=True)

        name = graphene.String(required=True)
        description = graphene.String()
        default = graphene.Boolean()
        start = graphene.DateTime()

    baseline = graphene.Field(Baseline)

    def mutate(self, info, project, **kwargs):
        project = pjt.Project.objects.get(pk=project)
        baseline = bl.Baseline.objects.create(creator_id=1, **kwargs)
        ge.DirectedGraphModelManager.connect_nodes(ge.Vertex.objects.get(id=baseline.pk), ge.Vertex.objects.get(id=project.pk), ge.EdgeType.objects.get(id='belongs_to'))
        return BaselineCreator(baseline=baseline)


class BaselineUpdater(graphene.Mutation):
    class Arguments:
        baseline = graphene.Int(required=True)
        propose_timeline = graphene.Boolean()

        name = graphene.String()
        description = graphene.String()
        default = graphene.Boolean()
        start = graphene.DateTime()

        partial_update = graphene.Boolean()
        partial_update_from = graphene.DateTime()
        

    baseline = graphene.Field(Baseline)

    def mutate(self, info, baseline, propose_timeline = None, partial_update = False, partial_update_from = None, **kwargs):
        bl.Baseline.objects.filter(pk=baseline).update(**kwargs)
        baseline = bl.Baseline.objects.get(id=baseline)
        if propose_timeline:
            edge = ge.Edge.objects.filter(source_vertex=baseline.pk, edge_type=ge.EdgeType.objects.get(id='belongs_to'))
            proposal = lib.ProposeAssigment(project_id=edge[0].target_vertex.pk, start=baseline.start)

            algo_time_start = time()
            # finish_date = proposal.assign_projects_infinite_resources(baseline.start)
            # finish_date = proposal.assign_projects_to_resources_first_free(one_worker_per_project=True)
            # finish_date = proposal.assign_projects_by_start_based_on_infinite_resources(one_worker_per_project=True)
            finish_date = proposal.assign_projects_by_start_based_on_infinite_resources(partial_update=partial_update, partial_update_from=partial_update_from, one_worker_per_project=True)
            algo_time_finish = time()

            print('Project finish timestamp: ' + str(finish_date))
            print('Calculation time [s]: ' + str(algo_time_finish - algo_time_start))
            print('Unassigned workers time during project: ' + str((proposal.av[proposal.av.project_id.isnull() & (proposal.av.start <= finish_date)].finish - proposal.av[proposal.av.project_id.isnull() & (proposal.av.start <= finish_date)].start).sum()))

            bl.Project.objects.filter(baseline=baseline.pk).delete() # TODO move to proposal.to_db()
            bl.Timeline.objects.filter(baseline=baseline.pk).delete() # TODO move to proposal.to_db()
            bl.ProjectDependency.objects.filter(baseline=baseline.pk).delete() # TODO move to proposal.to_db()
            proposal.to_db(baseline.pk)
        return BaselineUpdater(baseline=baseline)


class Mutation(graphene.ObjectType):
    create_baseline = BaselineCreator.Field()
    update_baseline = BaselineUpdater.Field()


