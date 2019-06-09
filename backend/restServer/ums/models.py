from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser

# Create your models here.

class User(AbstractBaseUser):
    email = models.EmailField(max_length = 100, unique = True, null = False)
    password = models.CharField(max_length = 300)
    createdDateTime = models.DateTimeField(auto_now_add = True)
    updateDateTime = models.DateTimeField(auto_now = True)
    isActive = models.BooleanField(null = False, default = True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']
    EMAIL_FIELD = 'email'
