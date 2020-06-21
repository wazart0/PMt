import graphene
from graphene_django.types import DjangoObjectType, ObjectType

import ge.models as ge



class Node(DjangoObjectType):
    class Meta():
        model = ge.Node


