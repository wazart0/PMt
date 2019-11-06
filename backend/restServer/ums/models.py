from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser



class User(AbstractBaseUser):
    creator_id = models.ForeignKey(null = True, to = 'self', on_delete = models.SET_NULL, db_column = 'creator_id', related_name = 'user_creator_id')
    created = models.DateTimeField(null = False, editable = False, auto_now_add = True)
    updated = models.DateTimeField(null = False, editable = False, auto_now = True)
    last_login = models.DateTimeField(null = True)

    email = models.EmailField(null = True, max_length = 100, unique = True)
    password = models.CharField(null = False, max_length = 300)
    is_active = models.BooleanField(null = False, default = True)
    name = models.CharField(null = True, max_length = 50)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']
    EMAIL_FIELD = 'email'

    objects = models.Manager()

    def save(self, force_insert = False, force_update = False, using = None, update_fields = None):
        print("User id: " + str(self.pk))  # TODO remove later
        if self.pk == None and self.creator_id == None:
                raise ValueError('Cannot create User, no creator_id field given.')
        models.Model.save(self, force_insert, force_update, using, update_fields)
        print("User id: " + str(self.pk))  # TODO remove later



class Group(models.Model):
    creator_id = models.ForeignKey(null = False, to = User, on_delete = models.PROTECT, db_column = 'creator_id', related_name = 'group_creator_id')
    created = models.DateTimeField(null = False, editable = False, auto_now_add = True)
    updated = models.DateTimeField(null = False, editable = False, auto_now = True)

    name = models.CharField(null = False, max_length = 50)
    description = models.TextField(null = True, default = None)
    parent_id = models.ForeignKey(null = True, to = 'self', on_delete = models.CASCADE, db_column = 'parent_id', related_name = 'group_parent_id')
    is_active = models.BooleanField(null = False, default = True)

    objects = models.Manager()

    # TODO improve protection against creator_id modification (editable = False - prevents possibility of instance creation)
    def save(self, force_insert = False, force_update = False, using = None, update_fields = None): 
        isCreated = True
        if self.pk is not None:
            isCreated = False

        print("Group id: " + str(self.pk))  # TODO remove later
        models.Model.save(self, force_insert, force_update, using, update_fields)
        print("Group id: " + str(self.pk))  # TODO remove later
        if (isCreated == True and self.pk is not None) or force_insert == True:
            groupPrivileges = GroupPrivileges.objects.all()
            for privilege in groupPrivileges:
                GroupAuthorization.objects.create(user_id = self.creator_id, group_privilege_id = privilege, group_id = self, authorizer_id = self.creator_id)


# class GroupMembers(models.Model):  -------->    moved to GroupAuthorization
#     group_id = models.ForeignKey(null = False, to = Group, on_delete = models.CASCADE, db_column = 'group_id', related_name = 'groupmembers_group_id')
#     user_id = models.ForeignKey(null = False, to = User, on_delete = models.CASCADE, db_column = 'user_id', related_name = 'groupmembers_user_id')
#     created = models.DateTimeField(null = False, auto_now_add = True)
#     inviter_id = models.ForeignKey(null = False, to = User, on_delete = models.PROTECT, db_column = 'inviter_id', related_name = 'groupmembers_inviter_id')
#     class Meta:
#         unique_together = ('group_id', 'user_id')
#     objects = models.Manager()


class GroupPrivileges(models.Model): # view, edit: name, add user, remove user, description, active/inactive, change childs parent, manage user privilege
    name = models.CharField(null = False, max_length = 50)
    code_name = models.CharField(null = False, max_length = 50, unique = True)
        
    objects = models.Manager()


class GroupAuthorization(models.Model):
    user_id = models.ForeignKey(null = False, to = User, on_delete = models.CASCADE, db_column = 'user_id', related_name = 'groupauthorization_user_id')
    group_privilege_id = models.ForeignKey(null = False, to = GroupPrivileges, on_delete = models.CASCADE, db_column = 'group_privilege_id', related_name = 'groupauthorization_group_privilege_id')
    group_id = models.ForeignKey(null = False, to = Group, on_delete = models.CASCADE, db_column = 'group_id', related_name = 'groupauthorization_group_id')
    created = models.DateTimeField(null = False, editable = False, auto_now_add = True)
    authorizer_id = models.ForeignKey(null = False, to = User, on_delete = models.PROTECT, db_column = 'authorizer_id', related_name = 'groupauthorization_authorizer_id')
    
    class Meta:
        unique_together = ('user_id', 'group_privilege_id', 'group_id')
        
    objects = models.Manager()
