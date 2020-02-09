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

    predecessors = graphene.List(lambda: Project)
    successors = graphene.List(lambda: Project)

    def resolve_predecessors(self, info):
        return pjt.Project.objects.get_predecessors(self.pk, edge_column='timeline_dependancy')

    def resolve_successors(self, info):
        return pjt.Project.objects.get_successors(self.pk, edge_column='timeline_dependancy')


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





class TimelineDependanceInput(graphene.InputObjectType):
    project_id = graphene.Int(required=True)
    dependance_type = graphene.String(required=True)


class ProjectCreator(graphene.Mutation):
    class Arguments:
        creator_id = graphene.Int(required=True)
        name = graphene.String(required=True)
        description = graphene.String()
        closed = graphene.Boolean()
        project_type = graphene.String(required=True)
        belongs_to = graphene.Int() # parent - choose final naming; group | project
        timeline_dependance = graphene.List(TimelineDependanceInput) # dependance from other projects

    project = graphene.Field(Project)

    def mutate(self, info, name, project_type, creator_id, description=None, closed=None, belongs_to=None, timeline_dependance=None):
        # project = pjt.Project.objects.create(creator_id=creator_id, name=name, project_type=project_type, description=description, closed=closed, belongs_to=belongs_to)
        project = pjt.Project.objects.create(creator_id=creator_id, name=name, description=description, closed=closed)
        # print(timeline_dependance)
        if timeline_dependance is not None:
            for i in timeline_dependance:
                ge.GraphModelManager.connect_nodes(project.id, ge.Node.objects.get(id=i['project_id']), timeline_dependancy=i['dependance_type'])
        return ProjectCreator(project=project)


class Mutation(graphene.ObjectType):
    create_project = ProjectCreator.Field()

