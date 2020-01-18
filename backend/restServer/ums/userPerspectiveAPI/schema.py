import graphene
from graphene_django.types import DjangoObjectType, ObjectType
from ums.models import *



class User(DjangoObjectType):
    class Meta:
        model = User


class Group(DjangoObjectType):
    class Meta:
        model = Group


class GroupPrivileges(DjangoObjectType):
    class Meta:
        model = GroupPrivileges


class GroupAuthorization(DjangoObjectType):
    class Meta:
        model = GroupAuthorization



class Query(ObjectType):
    user = graphene.Field(User, id=graphene.Int())
    group = graphene.Field(Group, id=graphene.Int())
    users = graphene.List(User)
    groups = graphene.List(Group)

    def resolve_actor(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return Actor.objects.get(pk=id)
        return None

    def resolve_movie(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return Movie.objects.get(pk=id)
        return None

    def resolve_actors(self, info, **kwargs):
        return Actor.objects.all()

    def resolve_movies(self, info, **kwargs):
        return Movie.objects.all()




schema = graphene.Schema(query=Query, mutation=None)
