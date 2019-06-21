from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import routers

from jobs.rawAPI.serializers import *

# Create your views here.

class JobDepthViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all().order_by('id')
    serializer_class = JobDepthSerializer


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


class MilestoneViewSet(viewsets.ModelViewSet):
    queryset = Milestone.objects.all()
    serializer_class = MilestoneSerializer


class BaselineViewSet(viewsets.ModelViewSet):
    queryset = Baseline.objects.all()
    serializer_class = BaselineSerializer


router = routers.SimpleRouter()
router.register(r'jobs', JobViewSet)
router.register(r'jobsDepth', JobDepthViewSet)
router.register(r'jobsStatus', JobStatusViewSet)
router.register(r'jobsType', JobTypeViewSet)
router.register(r'jobsStatusType', JobStatusTypeViewSet)
router.register(r'jobsMilestone', MilestoneViewSet)
router.register(r'jobsBaseline', BaselineViewSet)
