import graphene
from graphene_django.types import DjangoObjectType, ObjectType
from graphene_django.filter import DjangoFilterConnectionField

# from django.db.models.expressions import RawSQL
from django.db import connection

import baseline.models as bl
import graph_engine.models as ge
import project.models as pj



# TODO check to be added if the output is unique and protection against looped queries

def retrieve_data_from_db():
    return pj.Project.objects.all()


# def 



class TimeLine(ObjectType):
    pass




class Query(ObjectType):
    pass
    # project = graphene.Field(Project, id=graphene.Int())
    # projects = graphene.List(Project)
    
    # projectFilter = DjangoFilterConnectionField(ProjectFilter)

    # def resolve_project(self, info, **kwargs):
    #     id = kwargs.get('id')
    #     if id is not None:
    #         return pjt.Project.objects.get(pk=id)
    #     return None

    # def resolve_projects(self, info, **kwargs):
    #     return pjt.Project.objects.all()


