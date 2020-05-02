import graphene
from graphene_django.types import DjangoObjectType, ObjectType
from graphene_django.filter import DjangoFilterConnectionField

# from django.db.models.expressions import RawSQL
from django.db import connection

from time import time

import baseline.models as bl
# import baseline.models_virtual as bl_v
import graph_engine.models as ge
import project.models as pjt
import project.schema as pjt_sch
import libs.timeline.primitive_estimation as lib


# TODO check to be added if the output is unique and protection against looped queries

# def retrieve_data_from_db():
#     return pjt.Project.objects.all()



class ProjectTimeline(DjangoObjectType):
    class Meta:
        model = bl.Project
        exclude = ('baseline_id', 'id',)

    worktime_planned = graphene.String()


class Timeline(DjangoObjectType):
    class Meta:
        model = bl.Timeline
        exclude = ('baseline_id', 'id',)


class ProjectDependency(DjangoObjectType):
    class Meta:
        model = bl.ProjectDependency
        exclude = ('baseline_id', 'id',)


class Baseline(DjangoObjectType):
    class Meta:
        model = bl.Baseline
        fields = '__all__'
    id = graphene.Int(required=True)
    
    belongs_to = graphene.Field(pjt_sch.Project)
    timeline = graphene.List(Timeline)
    dependencies = graphene.List(ProjectDependency)
    projects = graphene.List(ProjectTimeline)

    def resolve_belongs_to(self, info):
        if len(ge.Edge.objects.filter(source_node_id=self.pk, belongs_to=True)) == 0:
            return None
        return pjt.Project.objects.get(pk=ge.Edge.objects.filter(source_node_id=self.pk, belongs_to=True)[0].target_node_id.pk)

    def resolve_timeline(self, info):
        return bl.Timeline.objects.filter(baseline_id=self.id)

    def resolve_dependencies(self, info):
        return bl.ProjectDependency.objects.filter(baseline_id=self.id)

    def resolve_projects(self, info):
        return bl.Project.objects.filter(baseline_id=self.id)




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

    baseline = graphene.Field(Baseline)

    def mutate(self, info, project_id, **kwargs):
        project = pjt.Project.objects.get(pk=project_id)
        baseline = bl.Baseline.objects.create(creator_id=1, **kwargs)
        ge.GraphModelManager.connect_nodes(ge.Node.objects.get(id=baseline.pk), ge.Node.objects.get(id=project.pk), belongs_to=True)
        return BaselineCreator(baseline=baseline)


class BaselineUpdater(graphene.Mutation):
    class Arguments:
        baseline = graphene.Int(required=True)
        propose_timeline = graphene.Boolean()
        name = graphene.String()
        description = graphene.String()
        default = graphene.Boolean()

    baseline = graphene.Field(Baseline)

    def mutate(self, info, baseline_id, propose_timeline = None, **kwargs):
        baseline = bl.Baseline.objects.get(id=baseline_id)
        if propose_timeline:
            edge = ge.Edge.objects.filter(source_node_id=baseline.pk, belongs_to=True)
            proposal = lib.ProposeAssigment(project_id=edge[0].target_node_id.pk)

            algo_time_start = time()
            finish_date = proposal.assign_projects_to_resources_first_free(one_worker_per_project=True)
            algo_time_finish = time()

            print('Project finish timestamp: ' + str(finish_date))
            print('Calculation time [s]: ' + str(algo_time_finish - algo_time_start))
            print('Unassigned workers time during project: ' + str((proposal.av[proposal.av.project_id.isnull() & (proposal.av.start <= finish_date)].finish - proposal.av[proposal.av.project_id.isnull() & (proposal.av.start <= finish_date)].start).sum()))

            bl.Project.objects.filter(baseline_id=baseline.pk).delete() # TODO move to proposal.to_db()
            bl.Timeline.objects.filter(baseline_id=baseline.pk).delete() # TODO move to proposal.to_db()
            bl.ProjectDependency.objects.filter(baseline_id=baseline.pk).delete() # TODO move to proposal.to_db()
            proposal.to_db(baseline.pk)
        return BaselineUpdater(baseline=baseline)


class Mutation(graphene.ObjectType):
    create_baseline = BaselineCreator.Field()
    update_baseline = BaselineUpdater.Field()


