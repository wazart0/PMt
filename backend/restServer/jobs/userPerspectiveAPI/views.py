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
    serializer_class = JobSerializer
    lookup_field = 'user_id'
    queryset = Job.objects.all()

    def list(self, request, user_id):
        if not User.objects.all().filter(id = user_id).exists():
            error404(request) 
        queryset = Job.objects.all().filter(creator = user_id).order_by('id')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)



router = routers.SimpleRouter()
router.register(r'(?P<user_id>.+)/jobs', JobViewSet)
