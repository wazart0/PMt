from rest_framework import serializers

from jobs.models import *



class BaselineSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Baseline
        fields = ('id', 'number', 'begin', 'worktime', 'end')
        read_only_fields = ('id', 'number', 'end')


class MilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = '__all__'
        read_only_fields = ('id', 'creator', 'created', 'updated')


class JobSerializer(serializers.ModelSerializer):
    defaultbaseline = BaselineSerializer()
    baselines = BaselineSerializer(many = True)
    milestones = MilestoneSerializer(many = True)

    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ('id', 'creator', 'created', 'updated')
        depth = 1

