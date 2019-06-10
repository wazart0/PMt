from rest_framework import serializers

from jobs.models import *


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ('url', 'id', 'parent', 'creator', 'created', 'updated', 'closed', 'childStatusGroup', 'status')


class JobStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobStatus
        fields = ('url', 'id', 'name', 'description')

class JobStatusGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobStatusGroup
        fields = ('url', 'id', 'name', 'description')

class JobStatusGroupListSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobStatusGroupList
        fields = ('url', 'jobStatusGroup', 'jobStatus')