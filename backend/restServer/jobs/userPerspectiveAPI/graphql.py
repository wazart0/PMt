import graphene
from graphene_django.types import DjangoObjectType, ObjectType
from jobs.models import *



class JobType(DjangoObjectType):
    class Meta:
        model = Job


class MilestoneType(DjangoObjectType):
    class Meta:
        model = Milestone


class JobAuthorizationType(DjangoObjectType):
    class Meta:
        model = JobAuthorization


class PrivilegesType(DjangoObjectType):
    class Meta:
        model = Privileges



# class Query(ObjectType):
#     job = graphene.Field(JobType, id=graphene.Int())
#     movie = graphene.Field(MovieType, id=graphene.Int())
#     jobs = graphene.List(ActorType)
#     movies = graphene.List(MovieType)

#     def resolve_actor(self, info, **kwargs):
#         id = kwargs.get('id')

#         if id is not None:
#             return Actor.objects.get(pk=id)

#         return None

#     def resolve_movie(self, info, **kwargs):
#         id = kwargs.get('id')

#         if id is not None:
#             return Movie.objects.get(pk=id)

#         return None

#     def resolve_actors(self, info, **kwargs):
#         return Actor.objects.all()

#     def resolve_movies(self, info, **kwargs):
#         return Movie.objects.all()