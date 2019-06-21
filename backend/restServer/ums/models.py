from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser

# Create your models here.

class User(AbstractBaseUser):
    created = models.DateTimeField(null = False, auto_now_add = True)
    updated = models.DateTimeField(null = False, auto_now = True)
    lastlogin = models.DateTimeField(null = True)

    email = models.EmailField(max_length = 100, unique = True, null = True)
    password = models.CharField(max_length = 300)
    isactive = models.BooleanField(null = False, default = True)
    firstname = models.CharField(null = True, max_length = 50)
    lastname = models.CharField(null = True, max_length = 50)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']
    EMAIL_FIELD = 'email'

    objects = models.Manager()


class UserGroup(models.Model):
    creator = models.ForeignKey(null = False, to = User, on_delete = models.PROTECT)
    created = models.DateTimeField(null = False, auto_now_add = True)
    updated = models.DateTimeField(null = False, auto_now = True)

    name = models.CharField(null = False, max_length = 50)
    description = models.TextField(null = True)
    parent = models.ForeignKey(to = 'self', null = True, on_delete = models.CASCADE)
    isactive = models.BooleanField(null = False, default = True)

    objects = models.Manager()


class GroupMembers(models.Model):
    usergroup = models.ForeignKey(null = False, to = UserGroup, on_delete = models.CASCADE)
    user = models.ForeignKey(null = False, to = User, on_delete = models.CASCADE)
    class Meta:
        unique_together = ('usergroup', 'user')

    objects = models.Manager()
