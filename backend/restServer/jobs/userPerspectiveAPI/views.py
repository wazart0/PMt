from django.shortcuts import render
from rest_framework import viewsets, mixins
from rest_framework import routers
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from jobs.userPerspectiveAPI.serializers import *



# def error404(request):
#     raise NotFound(detail="Error 404, page not found", code=404)


# def userAuthorizedJobs(userID):
#     return Job.objects.all().filter(creator_id = userID)
#     # return Job.objects.all()


# class JobViewSet(viewsets.GenericViewSet):
#     serializer_class = JobSerializer
#     queryset = Job.objects.all().filter(pk = 0)
#     lookup_field = 'user_id'

#     def list(self, request, user_id):
#         queryset = self.filter_queryset(userAuthorizedJobs(user_id))

#         page = self.paginate_queryset(queryset)
#         if page is not None:
#             serializer = self.get_serializer(page, many=True)
#             return self.get_paginated_response(serializer.data)

#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)



class JobViewSet(viewsets.GenericViewSet):
    queryset = Job.objects.none()
    serializer_class = JobSerializer

    @staticmethod
    def userAuthorizedQuery():
        return buildUniversalQueryTree(
            tableName = 'ums_job', 
            parentPrimaryKey = 'parent_id', 
            subQuery = '''
                    SELECT job_id FROM jobs_jobauthorization WHERE privilege_id = (
                        SELECT id FROM jobs_privileges WHERE code_name = %s) 
                    AND group_id = %s
                ''')

    # def get_queryset(self):
    #     return Group.objects.filter(id__in = RawSQL(
    #             self.userAuthorizedQuery(), 
    #             ['member', self.kwargs['context_user_id'], 'member', self.kwargs['context_user_id']])
    #         ).order_by('id')

    # def create(self, request, *args, **kwargs):
    #     return super().create(modifyRequest(request, 'creator_id', kwargs['context_user_id']), *args, **kwargs)

    



router = routers.SimpleRouter()
router.register(r'(?P<user_id>.+)/jobs', JobViewSet)
