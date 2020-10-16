from rest_framework import serializers

from ums.models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = ('id', 'email', 'password', 'is_active', 'name', 'created', 'updated', 'last_login', 'jakas') 
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'last_login')

    def is_valid(self, raise_exception=False):
        print(hasattr)
        return super().is_valid(raise_exception=raise_exception)


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'
        read_only_fields = ('id', 'creator_id', 'created', 'updated')


