from django.shortcuts import render
from rest_framework import viewsets, mixins
from rest_framework import routers
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from jobs.userPerspectiveAPI.serializers import *



# def error404(request):
#     raise NotFound(detail="Error 404, page not found", code=404)


def userAuthorizedJobs(userID):
    return Job.objects.all().filter(creator_id = userID)
    # return Job.objects.all()


class JobViewSet(viewsets.GenericViewSet):
    serializer_class = JobSerializer
    queryset = Job.objects.all().filter(pk = 0)
    lookup_field = 'user_id'

    def list(self, request, user_id):
        queryset = self.filter_queryset(userAuthorizedJobs(user_id))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)



router = routers.SimpleRouter()
router.register(r'(?P<user_id>.+)/jobs', JobViewSet)
