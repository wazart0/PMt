from rest_framework import serializers

from jobs.models import *



class BaselineSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Baseline
        fields = ('id', 'number', 'begin', 'interval', 'end')
        # read_only_fields = '__all__'


class JobSerializer(serializers.ModelSerializer):
    defaultbaseline = BaselineSerializer()
    baselines = BaselineSerializer(many = True)

    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ('id', 'creator', 'created', 'updated')
        depth = 1

