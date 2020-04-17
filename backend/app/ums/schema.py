import graphene
from graphene_django.types import DjangoObjectType, ObjectType
from graphene_django.filter import DjangoFilterConnectionField

import ums.models as ums



class User(DjangoObjectType):
    class Meta:
        model = ums.User
        exclude = ('password',)
    id = graphene.Int(required=True)


# class UserFilter(DjangoObjectType):
#     class Meta:
#         model = ums.User
#         interfaces = (graphene.Node,)
#         filter_fields = '__all__'


class Group(DjangoObjectType):
    class Meta:
        model = ums.Group
    id = graphene.Int(required=True)




class Query(ObjectType):
    user = graphene.Field(User, id=graphene.Int())
    users = graphene.List(User)
    # userFilter = DjangoFilterConnectionField(UserFilter)

    group = graphene.Field(Group, id=graphene.Int())
    groups = graphene.List(Group)
    

    def resolve_user(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return ums.User.objects.get(pk=id)
        return None

    def resolve_users(self, info, **kwargs):
        return ums.User.objects.all()

    def resolve_group(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return ums.Group.objects.get(pk=id)
        return None

    def resolve_groups(self, info, **kwargs):
        return ums.Group.objects.all()


class UserCreator(graphene.Mutation):
    class Arguments:
        creator_id = graphene.Int()
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        name = graphene.String()
    
    user = graphene.Field(User)

    def mutate(self, info, email, password, name=None, creator_id=None):
        user = ums.User.objects.create(creator_id=creator_id, email=email, password=password, name=name)
        return UserCreator(user=user)


class GroupCreator(graphene.Mutation):
    class Arguments:
        creator_id = graphene.Int(required=True)
        name = graphene.String(required=True)
        description = graphene.String()
        is_active = graphene.String()

    group = graphene.Field(Group)

    def mutate(self, info, name, creator_id, description=None, is_active=True):
        group = ums.Group.objects.create(creator_id=creator_id, name=name, description=description, is_active=is_active)
        return GroupCreator(group=group)



class Mutation(graphene.ObjectType):
    create_user = UserCreator.Field()
    create_group = GroupCreator.Field()

# schema = graphene.Schema(query=Query, mutation=None)
