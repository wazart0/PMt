from rest_framework import serializers
import copy

from ums.models import *



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'last_login')
        extra_kwargs = {
            'password': {'write_only': True},
        }



class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated')



class GroupAuthorizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupAuthorization
        fields = '__all__'
        read_only_fields = ('id', 'created')
    


class GroupPrivilegesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupPrivileges
        fields = '__all__'
        # read_only_fields = ('id', 'name', 'code_name')
