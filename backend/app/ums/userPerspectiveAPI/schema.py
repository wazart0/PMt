import graphene
from graphene_django.types import DjangoObjectType, ObjectType
import ums.models as ums


class User(DjangoObjectType):
    class Meta:
        model = ums.User



class Group(DjangoObjectType):
    class Meta:
        model = ums.Group


class GroupPrivileges(DjangoObjectType):
    class Meta:
        model = ums.GroupPrivileges



class GroupAuthorization(DjangoObjectType):
    class Meta:
        model = ums.GroupAuthorization



class Query(ObjectType):
    user = graphene.Field(User, id=graphene.Int())
    group = graphene.Field(Group, id=graphene.Int())
    users = graphene.List(User)
    groups = graphene.List(Group)

    def resolve_user(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return ums.User.objects.get(pk=id)
        return None

    def resolve_group(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return ums.Group.objects.get(pk=id)
        return None

    def resolve_users(self, info, **kwargs):
        return ums.User.objects.all()

    def resolve_groups(self, info, **kwargs):
        return ums.Group.objects.all()


# schema = graphene.Schema(query=Query, mutation=None)
