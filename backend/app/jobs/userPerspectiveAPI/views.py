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
            parentPrimaryKey = 'parent', 
            subQuery = '''
                    SELECT job FROM jobs_jobauthorization WHERE privilege = (
                        SELECT id FROM jobs_privileges WHERE code_name = %s) AND group IN ({userGroups})
                    GROUP BY job
                '''.format(userGroups = GroupViewSet.userAuthorizedQuery()))

    @staticmethod
    def userAuthorizedQueryArgs(contextUserID, privilege):
        return duplicateArgs(privilege, duplicateArgs('member', contextUserID))

    def get_queryset(self):
        return Job.objects.filter(id__in = RawSQL(
                self.userAuthorizedQuery(), 
                self.userAuthorizedQueryArgs(self.kwargs['context_user'], 'observer'))
            ).order_by('id')

    def create(self, request, *args, **kwargs): # TODO check permision (now every member can add) - only for parent ID
        return super().create(modifyRequest(request, 'creator', kwargs['context_user']), *args, **kwargs)



class JobAuthorizationViewSet(viewsets.ReadOnlyModelViewSet, mixins.CreateModelMixin, mixins.DestroyModelMixin):
    queryset = JobAuthorization.objects.none()
    serializer_class = JobAuthorizationSerializer

    @staticmethod
    def userAuthorizedQuery():
        return '''
            SELECT id FROM jobs_jobauthorization WHERE job = %s AND job IN ({userJobs})
        '''.format(userJobs = JobViewSet.userAuthorizedQuery())

    @staticmethod
    def userAuthorizedQueryArgs(contextUserID, jobID, privilege):
        return [jobID] + JobViewSet.userAuthorizedQueryArgs(contextUserID, privilege)

    def get_queryset(self):
        return JobAuthorization.objects.filter(id__in = RawSQL(
                self.userAuthorizedQuery(), 
                self.userAuthorizedQueryArgs(self.kwargs['context_user'], self.kwargs['job'], 'observer'))
            ).order_by('id')

    def create(self, request, *args, **kwargs): # TODO check permision (now every member can add); add request error if nothing returns from cursor query
        if 'group' in request.data:
            return super().create(
                modifyRequest(request, ['authorizer', 'job'], [kwargs['context_user'], kwargs['job']]),
                *args, 
                **kwargs)
        cursor = connection.cursor()
        cursor.execute('SELECT id FROM ums_group WHERE is_hidden = True AND creator = %s AND name = %s', [request.data['user'], str(request.data['user'])])
        row = cursor.fetchall()
        return super().create(
            modifyRequest(request, ['authorizer', 'job', 'group'], [kwargs['context_user'], kwargs['job'], row[0][0]]),
            *args, 
            **kwargs)
    


router = routers.SimpleRouter()
router.register(r'(?P<context_user>.+)/jobs', JobViewSet)
router.register(r'(?P<context_user>.+)/jobs/(?P<job>.+)/authorization', JobAuthorizationViewSet)
