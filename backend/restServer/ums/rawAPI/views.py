from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import routers

from ums.rawAPI.serializers import *

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer

 
class UserGroupViewSet(viewsets.ModelViewSet):
    queryset = UserGroup.objects.all()
    serializer_class = UserGroupSerializer

 
class GroupMembersViewSet(viewsets.ModelViewSet):
    queryset = GroupMembers.objects.all()
    serializer_class = GroupMembersSerializer

router = routers.SimpleRouter()
router.register(r'users', UserViewSet)
router.register(r'usersGroup', UserGroupViewSet)
router.register(r'usersGroupMembers', GroupMembersViewSet)
