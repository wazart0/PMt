from rest_framework import serializers

from ums.models import User


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'createdDateTime', 'updateDateTime', 'isActive')