from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import routers

from jobs.serializers import *

# Create your views here.

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all().order_by('id')
    serializer_class = JobSerializer

class JobStatusViewSet(viewsets.ModelViewSet):
    queryset = JobStatus.objects.all()
    serializer_class = JobStatusSerializer

class JobTypeViewSet(viewsets.ModelViewSet):
    queryset = JobType.objects.all()
    serializer_class = JobTypeSerializer

class JobStatusTypeViewSet(viewsets.ModelViewSet):
    queryset = JobStatusType.objects.all()
    serializer_class = JobStatusTypeSerializer


router = routers.SimpleRouter()
router.register(r'jobs', JobViewSet)
router.register(r'jobsStatus', JobStatusViewSet)
router.register(r'jobsType', JobTypeViewSet)
router.register(r'jobsStatusType', JobStatusTypeViewSet)
