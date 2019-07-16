from rest_framework import serializers

from ums.models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'created', 'updated', 'lastlogin', 'email', 'password', 'isactive', 'firstname', 'lastname')
        read_only_fields = ('id', 'created', 'updated', 'lastlogin')
        extra_kwargs = {
            'password': {'write_only': True}
        }


class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGroup
        fields = '__all__'
        read_only_fields = ('id', 'creator', 'created', 'updated')


class GroupMembersSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMembers
        fields = '__all__'
