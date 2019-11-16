from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, mixins, routers, status
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
            parentPrimaryKey = 'creator_id', 
            subQuery = '''SELECT id FROM ums_group WHERE id = %s''')

    def get_queryset(self):
        return User.objects.filter(id__in = RawSQL(
                self.userAuthorizedQuery(), 
                [self.kwargs['context_user_id'], self.kwargs['context_user_id']])
            ).order_by('id')

    def create(self, request, *args, **kwargs):
        return super().create(modifyRequest(request, 'creator_id', kwargs['context_user_id']), *args, **kwargs)



class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.none()
    serializer_class = GroupSerializer

    @staticmethod
    def userAuthorizedQuery(): # show groups in which user has chosen privilege
        return buildUniversalQueryTree(
            tableName = 'ums_group', 
            parentPrimaryKey = 'parent_id', 
            subQuery = '''
                    SELECT group_id FROM ums_groupauthorization WHERE group_privilege_id = (
                        SELECT id FROM ums_groupprivileges WHERE code_name = %s) AND user_id = %s
                ''')

    def get_queryset(self):
        return Group.objects.filter(id__in = RawSQL(
                self.userAuthorizedQuery(), 
                ['member', self.kwargs['context_user_id'], 'member', self.kwargs['context_user_id']])
            ).filter(is_hidden = False).order_by('id')

    def create(self, request, *args, **kwargs):
        return super().create(modifyRequest(request, 'creator_id', kwargs['context_user_id']), *args, **kwargs)



class GroupAuthorizationViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin):
    queryset = GroupAuthorization.objects.none()
    serializer_class = GroupAuthorizationSerializer

    @staticmethod
    def userAuthorizedQuery(): # TODO remove special groups (hidden)
        return '''
            SELECT id FROM ums_groupauthorization WHERE group_id = (
                SELECT group_id FROM ums_groupauthorization WHERE group_privilege_id = (
                    SELECT id FROM ums_groupprivileges WHERE code_name = %s)
                AND user_id = %s AND group_id = %s)
        '''

    def get_queryset(self):
        return GroupAuthorization.objects.filter(id__in = RawSQL(
                self.userAuthorizedQuery(), 
                ['member', self.kwargs['context_user_id'], self.kwargs['group_id']])
            ).order_by('id')

    def create(self, request, *args, **kwargs): # TODO check permision (now every member can add)
        return super().create(
            modifyRequest(request, ['authorizer_id', 'group_id'], [kwargs['context_user_id'], kwargs['group_id']]),
            *args, 
            **kwargs)



class GroupPrivilegesViewSet(viewsets.ReadOnlyModelViewSet, mixins.ListModelMixin):
    queryset = GroupPrivileges.objects.all()
    serializer_class = GroupPrivilegesSerializer
    


router = routers.SimpleRouter()
router.register(r'(?P<context_user_id>.+)/user', UserViewSet)
router.register(r'(?P<context_user_id>.+)/group', GroupViewSet)
router.register(r'(?P<context_user_id>.+)/group/(?P<group_id>.+)/authorization', GroupAuthorizationViewSet)
router.register(r'(?P<context_user_id>.+)/group/privileges/', GroupPrivilegesViewSet)
