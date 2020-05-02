from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, mixins, routers, status, generics
from rest_framework.response import Response
from rest_framework.settings import api_settings
from django.db.models import Q
from itertools import chain
from django.db.models.query import QuerySet
from django.db.models.expressions import RawSQL

from ums.userPerspectiveAPI.serializers import *
from libs.universalFunctions import *



class UserViewSet(viewsets.ReadOnlyModelViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin):
    queryset = User.objects.none()
    serializer_class = UserSerializer

    @staticmethod
    def userAuthorizedQuery():
        return buildUniversalQueryTree(
            tableName = 'ums_user', 
            parentPrimaryKey = 'creator', 
            subQuery = '''SELECT id FROM ums_group WHERE id = %s''')

    @staticmethod
    def userAuthorizedQueryArgs(contextUserID):
        return duplicateArgs(contextUserID)

    def get_queryset(self):
        return User.objects.filter(id__in = RawSQL(
                self.userAuthorizedQuery(), 
                self.userAuthorizedQueryArgs(self.kwargs['context_user']))
            ).order_by('id')

    def create(self, request, *args, **kwargs):
        return super().create(modifyRequest(request, 'creator', kwargs['context_user']), *args, **kwargs)



class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.none()
    serializer_class = GroupSerializer

    @staticmethod
    def userAuthorizedQuery(): # show groups in which user has chosen privilege
        return buildUniversalQueryTree(
            tableName = 'ums_group', 
            parentPrimaryKey = 'parent', 
            subQuery = '''
                    SELECT group FROM ums_groupauthorization WHERE group_privilege = (
                        SELECT id FROM ums_groupprivileges WHERE code_name = %s) AND user = %s
                ''')

    @staticmethod
    def userAuthorizedQueryArgs(contextUserID, privilege):
        return duplicateArgs(privilege, contextUserID)

    def get_queryset(self):
        return Group.objects.filter(id__in = RawSQL(
                self.userAuthorizedQuery(), 
                self.userAuthorizedQueryArgs(self.kwargs['context_user'], 'member'))
            ).filter(is_hidden = False).order_by('id')

    def create(self, request, *args, **kwargs): # TODO check permision (now every member can add) - only for parent ID
        return super().create(modifyRequest(request, 'creator', kwargs['context_user']), *args, **kwargs)



# class GroupAuthorizationViewSet(viewsets.ReadOnlyModelViewSet, mixins.CreateModelMixin, mixins.DestroyModelMixin):
#     queryset = GroupAuthorization.objects.none()
#     serializer_class = GroupAuthorizationSerializer

#     @staticmethod
#     def userAuthorizedQuery():
#         return '''
#             SELECT id FROM ums_groupauthorization WHERE group = %s AND group IN ({userGroups})
#         '''.format(userGroups = GroupViewSet.userAuthorizedQuery())

#     @staticmethod
#     def userAuthorizedQueryArgs(contextUserID, groupID, privilege):
#         return [groupID] + GroupViewSet.userAuthorizedQueryArgs(contextUserID, privilege)

#     def get_queryset(self):
#         return GroupAuthorization.objects.filter(id__in = RawSQL(
#                 self.userAuthorizedQuery(),
#                 self.userAuthorizedQueryArgs(self.kwargs['context_user'], self.kwargs['group'], 'member'))
#             ).order_by('id')

#     def create(self, request, *args, **kwargs): # TODO check permision (now every member can add)
#         return super().create(
#             modifyRequest(request, ['authorizer', 'group'], [kwargs['context_user'], kwargs['group']]),
#             *args, 
#             **kwargs)



# class GroupPrivilegesViewSet(viewsets.ReadOnlyModelViewSet, mixins.ListModelMixin):
#     queryset = GroupPrivileges.objects.all()
#     serializer_class = GroupPrivilegesSerializer
    


router = routers.SimpleRouter()
router.register(r'(?P<context_user>.+)/user', UserViewSet)
router.register(r'(?P<context_user>.+)/group', GroupViewSet)
router.register(r'(?P<context_user>.+)/group/(?P<group>.+)/authorization', GroupAuthorizationViewSet)
router.register(r'(?P<context_user>.+)/group/privileges/', GroupPrivilegesViewSet)
