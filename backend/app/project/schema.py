import graphene
from graphene_django.types import DjangoObjectType, ObjectType
from graphene_django.filter import DjangoFilterConnectionField

import project.models as pjt
import graph_engine.models as ge





class ProjectFilter(DjangoObjectType):
    class Meta:
        model = pjt.Project
        interfaces = (graphene.Node,)
        filter_fields = '__all__'


class Milestone(DjangoObjectType):
    class Meta:
        model = pjt.Milestone
    id = graphene.Int(required=True)


class Project(DjangoObjectType):
    class Meta:
        model = pjt.Project
    id = graphene.Int(required=True)

    worktime_planned = graphene.String()

    predecessors = graphene.List(lambda: Project)
    successors = graphene.List(lambda: Project)
    belongs_to = graphene.Field(lambda: Project)
    has_belonger = graphene.Boolean()

    def resolve_predecessors(self, info): # TODO divide into SS/FF/SF/FS
        return pjt.Project.objects.get_predecessors(self.pk, edge_column='timeline_dependency')

    def resolve_successors(self, info): # TODO divide into SS/FF/SF/FS
        return pjt.Project.objects.get_successors(self.pk, edge_column='timeline_dependency')

    def resolve_belongs_to(self, info):
        if len(ge.Edge.objects.filter(source_node=self.pk, belongs_to=True)) == 0:
            return None
        return pjt.Project.objects.get(pk=ge.Edge.objects.filter(source_node=self.pk, belongs_to=True)[0].target_node.pk)
    
    def resolve_has_belonger(self, info):
        # self.has_belonger = self.has_belonger_()
        return len(ge.Edge.objects.filter(target_node=self.pk, belongs_to=True)) != 0



class Query(ObjectType):
    project = graphene.Field(Project, id=graphene.Int())
    projects = graphene.List(Project)
    
    projectFilter = DjangoFilterConnectionField(ProjectFilter)

    def resolve_project(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return pjt.Project.objects.get(pk=id)
        return None

    def resolve_projects(self, info, **kwargs):
        return pjt.Project.objects.all()





class TimelinedependenceInput(graphene.InputObjectType):
    project = graphene.Int(required=True)
    dependence_type = graphene.String(required=True)


class ProjectCreator(graphene.Mutation):
    class Arguments:
        creator = graphene.Int(required=True)
        name = graphene.String(required=True)
        description = graphene.String()
        closed = graphene.Boolean()
        project_type = graphene.String(required=True)
        belongs_to = graphene.Int() # parent - choose final naming; group | project
        worktime_planned = graphene.String()
        predecessors = graphene.List(TimelinedependenceInput) # dependence from other projects

    project = graphene.Field(Project)

    def mutate(self, info, name, project_type, creator, description=None, closed=None, belongs_to=None, predecessors=None, worktime_planned=None):
        project = pjt.Project.objects.create(creator_id=creator, name=name, description=description, closed=closed, worktime_planned=worktime_planned)
        # print(predecessors)
        if belongs_to is not None:
            ge.GraphModelManager.connect_nodes(project.id, ge.Node.objects.get(id=belongs_to), belongs_to=True)
        if predecessors is not None:
            for i in predecessors:
                ge.GraphModelManager.connect_nodes(project.id, ge.Node.objects.get(id=i['project']), timeline_dependency=i['dependence_type'])
        return ProjectCreator(project=project)


class ProjectUpdater(graphene.Mutation):
    class Arguments:
        project = graphene.Int(required=True)
        predecessors = graphene.List(TimelinedependenceInput) # dependence from other projects

    project = graphene.Field(Project)

    def mutate(self, info, project, predecessors=None):
        project = pjt.Project.objects.get(pk=project)
        if predecessors is not None:
            for i in predecessors:
                edges = ge.Edge.objects.filter(source_node=i['project'], target_node=project.pk)
                if len(edges) == 0:
                    ge.GraphModelManager.connect_nodes(ge.Node.objects.get(id=i['project']), ge.Node.objects.get(id=project.pk), timeline_dependency=i['dependence_type'])
                else:
                    edges[0].timeline_dependency = i['dependence_type']
        return ProjectUpdater(project=project)



class Mutation(graphene.ObjectType):
    create_project = ProjectCreator.Field()
    update_project = ProjectUpdater.Field()
