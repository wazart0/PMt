from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, mixins, routers, status
from rest_framework.response import Response
from rest_framework.settings import api_settings
from django.db.models import Q
from itertools import chain
from django.db.models.query import QuerySet
from django.db.models.expressions import RawSQL

from ums.userPerspectiveAPI.serializers import *


def modifyRequest(request, field, value):
    mutable = request.POST._mutable
    request.POST._mutable = True
    if isinstance(field, list) and isinstance(value, list):
        if len(field) == len(value):
            for i in range(len(field)):
                request.data[field[i]] = str(value[i])
        else:
            raise ValueError('modifyRequest(): some error in querry')
    else:
        request.data[field] = str(value) 
    request.POST._mutable = mutable
    return request


def buildQueryTree(tableName, parentColumnName, columns = '*'):
    return \
        "WITH RECURSIVE nodes AS (" + \
        "SELECT s1." + columns + " " + \
        " FROM " + tableName + " s1 WHERE " + parentColumnName + " = %s" \
        "    UNION " + \
        "SELECT s2." + columns + "" + \
        " FROM " + tableName + " s2, nodes s1 WHERE s2." + parentColumnName + " = s1.id" + \
        ")" + \
        " SELECT " + columns + " FROM nodes " + \
        "    UNION " + \
        " SELECT " + columns + " FROM " + tableName + " WHERE ID = %s"


    

def userAuthorizedUMS(userID):
    return User.objects.filter(id__in = RawSQL(buildQueryTree('ums_user', 'creator_id', 'id'), [userID, userID]))


def userAuthorizedGroup(userID, privilege = 'member'): # tree view has to be added in here
    return Group.objects.filter(id__in = RawSQL('''select ums_group.id from ums_group inner join (select * from ums_groupauthorization where group_privilege_id = (select id from ums_groupprivileges where code_name = %s) and user_id = %s) as tmp on ums_group.id = tmp.group_id''', [privilege, userID]))



class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        return userAuthorizedUMS(self.kwargs['requesting_user_id']).order_by('id')

    def create(self, request, *args, **kwargs):
        return super().create(modifyRequest(request, 'creator_id', kwargs['requesting_user_id']), *args, **kwargs)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def get_queryset(self):
        return userAuthorizedGroup(self.kwargs['requesting_user_id']).order_by('id')

    def create(self, request, *args, **kwargs):
        return super().create(modifyRequest(request, 'creator_id', kwargs['requesting_user_id']), *args, **kwargs)


router = routers.SimpleRouter()
router.register(r'(?P<requesting_user_id>.+)/user', UserViewSet)
router.register(r'(?P<requesting_user_id>.+)/group', GroupViewSet)
