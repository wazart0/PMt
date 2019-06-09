from django.shortcuts import render
from rest_framework import viewsets

from jobs.serializers import JobSerializer
from jobs.models import Job

# Create your views here.

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer