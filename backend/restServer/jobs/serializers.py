from rest_framework import serializers

from jobs.models import Job


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ('id', 'parent', 'creator', 'created', 'updated', 'closed', 'childStatusGroup', 'status')