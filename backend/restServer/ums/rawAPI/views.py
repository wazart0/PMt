from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import routers

from ums.rawAPI.serializers import *

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer

 
class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

 


router = routers.SimpleRouter()
router.register(r'users', UserViewSet)
router.register(r'usersGroup', GroupViewSet)
