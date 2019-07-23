from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser



class User(AbstractBaseUser):
    creator_id = models.ForeignKey(null = True, to = 'self', on_delete = models.SET_NULL, db_column = 'creator_id', related_name = 'user_creator_id')
    created = models.DateTimeField(null = False, auto_now_add = True)
    updated = models.DateTimeField(null = False, auto_now = True)
    last_login = models.DateTimeField(null = True)

    email = models.EmailField(null = True, max_length = 100, unique = True)
    password = models.CharField(null = False, max_length = 300)
    is_active = models.BooleanField(null = False, default = True)
    first_name = models.CharField(null = True, max_length = 50)
    last_name = models.CharField(null = True, max_length = 50)

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
            ug = Group.objects.create(creator = self.creator_id, name = str(self.pk), parent = None)
            GroupMembers.objects.create(inviter = self, user = self, usergroup = ug)



class Group(models.Model):
    creator_id = models.ForeignKey(null = True, to = User, on_delete = models.PROTECT, db_column = 'creator_id', related_name = 'group_creator_id')
    created = models.DateTimeField(null = False, auto_now_add = True)
    updated = models.DateTimeField(null = False, auto_now = True)

    name = models.CharField(null = False, max_length = 50)
    description = models.TextField(null = True, default = None)
    parent_id = models.ForeignKey(null = True, to = 'self', on_delete = models.CASCADE, db_column = 'parent_id', related_name = 'group_parent_id')
    is_active = models.BooleanField(null = False, default = True)

    objects = models.Manager()


class GroupMembers(models.Model):
    group_id = models.ForeignKey(null = False, to = Group, on_delete = models.CASCADE, db_column = 'group_id', related_name = 'groupmembers_group_id')
    user_id = models.ForeignKey(null = False, to = User, on_delete = models.CASCADE, db_column = 'user_id', related_name = 'groupmembers_user_id')
    created = models.DateTimeField(null = False, auto_now_add = True)
    inviter_id = models.ForeignKey(null = False, to = User, on_delete = models.PROTECT, db_column = 'inviter_id', related_name = 'groupmembers_inviter_id')

    class Meta:
        unique_together = ('group_id', 'user_id')

    objects = models.Manager()


class GroupPrivileges(models.Model): # three user types per job (manager, normal, viewer) defined individually 
    name = models.CharField(null = False, max_length = 50)
    code_name = models.CharField(null = False, max_length = 50, unique = True)
        
    objects = models.Manager()


class GroupAuthorization(models.Model):
    user_id = models.ForeignKey(null = False, to = User, on_delete = models.CASCADE, editable = False, db_column = 'user_id', related_name = 'groupauthorization_user_id')
    group_privilege_id = models.ForeignKey(null = False, to = GroupPrivileges, on_delete = models.CASCADE, editable = False, db_column = 'group_privilege_id', related_name = 'groupauthorization_group_privilege_id')
    group_id = models.ForeignKey(null = False, to = Group, on_delete = models.CASCADE, editable = False, db_column = 'group_id', related_name = 'groupauthorization_group_id')
    
    class Meta:
        unique_together = ('user_id', 'group_privilege_id', 'group_id')
        
    objects = models.Manager()
