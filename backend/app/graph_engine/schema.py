import graphene
from graphene_django.types import DjangoObjectType, ObjectType

import graph_engine.models as ge



class Node(DjangoObjectType):
    class Meta():
        model = ge.Node


