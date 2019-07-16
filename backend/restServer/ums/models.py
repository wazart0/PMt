from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser



class User(AbstractBaseUser):
    creator = models.ForeignKey(null = True, to = 'self', on_delete = models.SET_NULL, related_name = 'usercreator')
    created = models.DateTimeField(null = False, auto_now_add = True)
    updated = models.DateTimeField(null = False, auto_now = True)
    lastlogin = models.DateTimeField(null = True)

    email = models.EmailField(null = True, max_length = 100, unique = True)
    password = models.CharField(null = False, max_length = 300)
    isactive = models.BooleanField(null = False, default = True)
    firstname = models.CharField(null = True, max_length = 50)
    lastname = models.CharField(null = True, max_length = 50)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']
    EMAIL_FIELD = 'email'

    objects = models.Manager()

    def save(self, force_insert = False, force_update = False, using = None, update_fields = None):
        isCreated = False
        if self.pk is None:
            isCreated = True
        models.Model.save(self, force_insert, force_update, using, update_fields)
        if (isCreated == True and self.pk is not None) or force_insert == True:
            ug = UserGroup.objects.create(creator_id = self.creator, name = str(self.pk), parent = None)
            GroupMembers.objects.create(inviter = self, user = self, usergroup = ug)



class UserGroup(models.Model):
    creator = models.ForeignKey(null = True, to = User, on_delete = models.PROTECT)
    created = models.DateTimeField(null = False, auto_now_add = True)
    updated = models.DateTimeField(null = False, auto_now = True)

    name = models.CharField(null = False, max_length = 50)
    description = models.TextField(null = True, default = None)
    parent = models.ForeignKey(null = True, to = 'self', on_delete = models.CASCADE)
    isactive = models.BooleanField(null = False, default = True)

    objects = models.Manager()


class GroupMembers(models.Model):
    usergroup = models.ForeignKey(null = False, to = UserGroup, on_delete = models.CASCADE)
    user = models.ForeignKey(null = False, to = User, on_delete = models.CASCADE)
    created = models.DateTimeField(null = False, auto_now_add = True)
    inviter = models.ForeignKey(null = False, to = User, on_delete = models.PROTECT, related_name = 'groupinviter')

    class Meta:
        unique_together = ('usergroup', 'user')

    objects = models.Manager()


class GroupPrivileges(models.Model): # three user types per job (manager, normal, viewer) defined individually 
    name = models.CharField(null = False, max_length = 50)
    codename = models.CharField(null = False, max_length = 50)
        
    objects = models.Manager()


class GroupAuth(models.Model):
    user = models.ForeignKey(null = False, to = User, on_delete = models.CASCADE, editable = False)
    groupprivileges = models.ForeignKey(null = False, to = GroupPrivileges, on_delete = models.CASCADE, editable = False)
    usergroup = models.ForeignKey(null = False, to = UserGroup, on_delete = models.CASCADE, editable = False)
    
    class Meta:
        unique_together = ('user', 'groupprivileges', 'usergroup')
        
    objects = models.Manager()
