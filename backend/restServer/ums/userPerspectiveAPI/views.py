from django.shortcuts import render
from rest_framework import viewsets, mixins, routers, status
from rest_framework.response import Response
from rest_framework.settings import api_settings
from django.db.models import Q
from itertools import chain

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


def buildQueryTree(tableName, parentColumnName, rootID, columns='*'):
    return \
        "WITH RECURSIVE nodes AS (" + \
        "SELECT s1." + columns + " " + \
        "FROM " + tableName + " s1 WHERE " + parentColumnName + " = " + str(rootID) + \
        "    UNION " + \
        "SELECT s2." + columns + "" + \
        "FROM " + tableName + " s2, nodes s1 WHERE s2." + parentColumnName + " = s1.id" + \
        ")" + \
        "SELECT " + columns + " FROM nodes " + \
        "    UNION " + \
        "SELECT " + columns + " FROM " + tableName + " WHERE ID = " + str(rootID) + ";"


    

def userAuthorizedUMS(userID):
    return User.objects.raw(buildQueryTree('ums_user', 'creator_id', userID))


def userAuthorizedGroup(userID, privilege = 'member'): # tree view has to be added in here
    return Group.objects.raw('''select ums_group.* from ums_group inner join (select * from ums_groupauthorization where group_privilege_id = (select id from ums_groupprivileges where code_name = %s) and user_id = %s) as tmp on ums_group.id = tmp.group_id;''', [privilege, userID])



class UserViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = User.objects.all().filter(pk = 0)
    serializer_class = UserSerializer
    lookup_field = 'userID'

    def list(self, request, userID):
        queryset = self.filter_queryset(userAuthorizedUMS(userID))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many = True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many = True)
        return Response(serializer.data)

    def create(self, request, userID, *args, **kwargs):
        return super().create(modifyRequest(request, 'creator_id', userID), *args, **kwargs)


class GroupViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = Group.objects.all().filter(pk = 0)
    serializer_class = GroupSerializer
    lookup_field = 'userID'

    def list(self, request, userID):
        queryset = self.filter_queryset(userAuthorizedGroup(userID))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many = True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many = True)
        return Response(serializer.data)

    # def create(self, request, userID, *args, **kwargs):
    #     return super().create(modifyRequest(request, 'creator_id', userID), *args, **kwargs)


router = routers.SimpleRouter()
router.register(r'(?P<userID>.+)/user', UserViewSet)
router.register(r'(?P<userID>.+)/group', GroupViewSet)
