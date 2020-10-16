from rest_framework import serializers

from jobs.models import *



class BaselineSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Baseline
        fields = ('id', 'number', 'start', 'worktime', 'finish')
        read_only_fields = ('id', 'number', 'finish')


class MilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = '__all__'
        read_only_fields = ('id', 'creator_id', 'created', 'updated')
        


class JobSerializer(serializers.ModelSerializer):
    # default_baseline_id = BaselineSerializer()
    # baselines = BaselineSerializer(many = True)
    # milestones = MilestoneSerializer(many = True)

    class Meta:
        model = Job
        fields = '__all__'
        # read_only_fields = ('id', 'created', 'updated')
        # depth = 1



class JobAuthorizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobAuthorization
        fields = '__all__'
        read_only_fields = ('id', 'created')