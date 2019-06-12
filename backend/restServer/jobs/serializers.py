from rest_framework import serializers

from jobs.models import *


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'
        depth = 1


class JobStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobStatus
        fields = '__all__'

class JobStatusGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobStatusGroup
        fields = '__all__'

class JobStatusGroupListSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobStatusGroupList
        fields = '__all__'
