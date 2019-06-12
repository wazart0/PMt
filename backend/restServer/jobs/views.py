from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import routers

from jobs.serializers import *
from jobs.models import *

# Create your views here.

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer

class JobStatusViewSet(viewsets.ModelViewSet):
    queryset = JobStatus.objects.all()
    serializer_class = JobStatusSerializer

class JobStatusGroupViewSet(viewsets.ModelViewSet):
    queryset = JobStatusGroup.objects.all()
    serializer_class = JobStatusGroupSerializer

class JobStatusGroupListViewSet(viewsets.ModelViewSet):
    queryset = JobStatusGroupList.objects.all()
    serializer_class = JobStatusGroupListSerializer


router = routers.DefaultRouter()
router.register(r'', JobViewSet)
router.register(r'status', JobStatusViewSet)
router.register(r'statusGroup', JobStatusGroupViewSet)
router.register(r'statusGroupList', JobStatusGroupListViewSet)