from django.shortcuts import render
from rest_framework import viewsets, mixins
from rest_framework import routers
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.db import connection
from django.db.models.expressions import RawSQL

from jobs.userPerspectiveAPI.serializers import *
from ums.userPerspectiveAPI.views import GroupViewSet
from libs.universalFunctions import *



class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.none()
    serializer_class = JobSerializer

    @staticmethod
    def userAuthorizedQuery():
        return buildUniversalQueryTree(
            tableName = 'jobs_job', 
            parentPrimaryKey = 'parent_id', 
            subQuery = '''
                    SELECT job_id FROM jobs_jobauthorization WHERE privilege_id = (
                        SELECT id FROM jobs_privileges WHERE code_name = %s) AND group_id IN ({userGroups})
                    GROUP BY job_id
                '''.format(userGroups = GroupViewSet.userAuthorizedQuery()))

    @staticmethod
    def userAuthorizedQueryArgs(contextUserID, privilege):
        return duplicateArgs(privilege, duplicateArgs('member', contextUserID))

    def get_queryset(self):
        return Job.objects.filter(id__in = RawSQL(
                self.userAuthorizedQuery(), 
                self.userAuthorizedQueryArgs(self.kwargs['context_user_id'], 'observer'))
            ).order_by('id')

    def create(self, request, *args, **kwargs): # TODO check permision (now every member can add) - only for parent ID
        return super().create(modifyRequest(request, 'creator_id', kwargs['context_user_id']), *args, **kwargs)



class JobAuthorizationViewSet(viewsets.ReadOnlyModelViewSet, mixins.CreateModelMixin, mixins.DestroyModelMixin):
    queryset = JobAuthorization.objects.none()
    serializer_class = JobAuthorizationSerializer

    @staticmethod
    def userAuthorizedQuery():
        return '''
            SELECT id FROM jobs_jobauthorization WHERE job_id = %s AND job_id IN ({userJobs})
        '''.format(userJobs = JobViewSet.userAuthorizedQuery())

    @staticmethod
    def userAuthorizedQueryArgs(contextUserID, jobID, privilege):
        return [jobID] + JobViewSet.userAuthorizedQueryArgs(contextUserID, privilege)

    def get_queryset(self):
        return JobAuthorization.objects.filter(id__in = RawSQL(
                self.userAuthorizedQuery(), 
                self.userAuthorizedQueryArgs(self.kwargs['context_user_id'], self.kwargs['job_id'], 'observer'))
            ).order_by('id')

    def create(self, request, *args, **kwargs): # TODO check permision (now every member can add); add request error if nothing returns from cursor query
        if 'group_id' in request.data:
            return super().create(
                modifyRequest(request, ['authorizer_id', 'job_id'], [kwargs['context_user_id'], kwargs['job_id']]),
                *args, 
                **kwargs)
        cursor = connection.cursor()
        cursor.execute('SELECT id FROM ums_group WHERE is_hidden = True AND creator_id = %s AND name = %s', [request.data['user_id'], str(request.data['user_id'])])
        row = cursor.fetchall()
        return super().create(
            modifyRequest(request, ['authorizer_id', 'job_id', 'group_id'], [kwargs['context_user_id'], kwargs['job_id'], row[0][0]]),
            *args, 
            **kwargs)
    


router = routers.SimpleRouter()
router.register(r'(?P<context_user_id>.+)/jobs', JobViewSet)
router.register(r'(?P<context_user_id>.+)/jobs/(?P<job_id>.+)/authorization', JobAuthorizationViewSet)
