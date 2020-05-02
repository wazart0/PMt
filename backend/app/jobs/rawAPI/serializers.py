from rest_framework import serializers

from jobs.models import *


class JobDepthSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ('id', 'creator', 'created', 'updated')
        depth = 1

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ('id', 'creator', 'created', 'updated')
        # depth = 1


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = '__all__'


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = '__all__'


class TypeStatusesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeStatuses
        fields = '__all__'
        # depth = 1


class MilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = '__all__'


class BaselineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Baseline
        fields = '__all__'
