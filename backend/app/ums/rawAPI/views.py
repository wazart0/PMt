from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import routers

from ums.rawAPI.serializers import *
from libs.universalFunctions import modifyRequest

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer

    # def create(self, request, *args, **kwargs):
    #     return super().create(modifyRequest(request, 'creator_id', 4), *args, **kwargs)

 
class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

 


router = routers.SimpleRouter()
router.register(r'users', UserViewSet)
router.register(r'usersGroup', GroupViewSet)
