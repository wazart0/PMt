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


class StatusViewSet(viewsets.ModelViewSet):
    queryset = Status.objects.all()
    serializer_class = StatusSerializer


class TypeViewSet(viewsets.ModelViewSet):
    queryset = Type.objects.all()
    serializer_class = TypeSerializer


class TypeStatusesViewSet(viewsets.ModelViewSet):
    queryset = TypeStatuses.objects.all()
    serializer_class = TypeStatusesSerializer


class MilestoneViewSet(viewsets.ModelViewSet):
    queryset = Milestone.objects.all()
    serializer_class = MilestoneSerializer


class BaselineViewSet(viewsets.ModelViewSet):
    queryset = Baseline.objects.all()
    serializer_class = BaselineSerializer


router = routers.SimpleRouter()
router.register(r'jobs', JobViewSet)
router.register(r'jobsDepth', JobDepthViewSet)
router.register(r'jobsStatus', StatusViewSet)
router.register(r'jobsType', TypeViewSet)
router.register(r'jobsTypeStatuses', TypeStatusesViewSet)
router.register(r'jobsMilestone', MilestoneViewSet)
router.register(r'jobsBaseline', BaselineViewSet)
