from django.shortcuts import render
from rest_framework import viewsets
from ums.serializers import UserSerializer
from ums.models import User

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer

 