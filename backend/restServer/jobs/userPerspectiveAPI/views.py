from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import routers
from rest_framework.response import Response
from rest_framework.exceptions import NotFound


from jobs.userPerspectiveAPI.serializers import *


# Create your views here.

# from rest_framework.decorators import api_view
# from rest_framework.response import Response

def error404(request):
    raise NotFound(detail="Error 404, page not found", code=404)


class JobViewSet(viewsets.GenericViewSet):
    queryset = Job.test.get_queryset(0).order_by('id')
    serializer_class = JobSerializer
    lookup_field = 'user_id'

    def list(self, request, user_id):
        if User.objects.get(id = user_id) == 0:
            error404(request) # TODO check if the user exists
        queryset = Job.test.get_queryset(user_id).order_by('id')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)



router = routers.SimpleRouter()
router.register(r'(?P<user_id>.+)/jobs', JobViewSet)
