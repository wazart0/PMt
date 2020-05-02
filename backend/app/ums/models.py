from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser

from graph_engine.models import Node, NodeModelManager



class User(AbstractBaseUser):
    node_type = 'user'
    objects = NodeModelManager()
    id = models.OneToOneField(to=Node, primary_key=True, editable=False, db_column='id', related_name='user_id', on_delete=models.PROTECT)

    created = models.DateTimeField(null = False, editable = False, auto_now_add = True)
    updated = models.DateTimeField(null = False, editable = False, auto_now = True) # TODO special logger has to be implemented - later remove
    last_login = models.DateTimeField(null = True) # TODO special logger has to be implemented - later remove

    email = models.EmailField(null = True, max_length = 100, unique = True)
    password = models.CharField(null = False, max_length = 300)
    is_active = models.BooleanField(null = False, default = True)
    name = models.CharField(null = True, max_length = 50)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']
    EMAIL_FIELD = 'email'



class Group(models.Model):
    node_type = 'group'
    objects = NodeModelManager()
    id = models.OneToOneField(to=Node, primary_key=True, editable=False, db_column='id', related_name='group_id', on_delete=models.PROTECT)

    created = models.DateTimeField(null = False, editable = False, auto_now_add = True)
    updated = models.DateTimeField(null = False, editable = False, auto_now = True) # TODO special logger has to be implemented - later remove

    name = models.CharField(null = False, max_length = 50)
    description = models.TextField(null = True, default = None)
    is_active = models.BooleanField(null = False, default = True)
    # group_type -> group | team | organization

    def add_member(self, user_id):
        user = User.objects.get(id=user_id)
        Node.objects.connect_nodes(self.id, user.id, member=True)
        return self


    # TODO improve protection against creator_id modification (editable = False - prevents possibility of instance creation)
    # def save(self, force_insert = False, force_update = False, using = None, update_fields = None): 
    #     isCreated = True
    #     if self.pk is not None:
    #         isCreated = False
    #     models.Model.save(self, force_insert, force_update, using, update_fields)
    #     if (isCreated == True and self.pk is not None) or force_insert == True:
    #         groupPrivileges = GroupPrivileges.objects.all()
    #         for privilege in groupPrivileges:
    #             GroupAuthorization.objects.create(user = self.creator_id, group_privilege = privilege, group = self, authorizer = self.creator_id)



# class GroupPrivileges(models.Model): # view, edit: name, add user, remove user, description, active/inactive, change childs parent, manage user privilege
#     name = models.CharField(null = False, max_length = 50)
#     code_name = models.CharField(null = False, max_length = 50, unique = True)
        
#     objects = models.Manager()



# class GroupAuthorization(models.Model):
#     user = models.ForeignKey(null = False, to = User, on_delete = models.CASCADE, db_column = 'user_id', related_name = 'groupauthorization_user_id')
#     group_privilege = models.ForeignKey(null = False, to = GroupPrivileges, on_delete = models.CASCADE, db_column = 'group_privilege_id', related_name = 'groupauthorization_group_privilege_id')
#     group = models.ForeignKey(null = False, to = Group, on_delete = models.CASCADE, db_column = 'group_id', related_name = 'groupauthorization_group_id')
#     created = models.DateTimeField(null = False, editable = False, auto_now_add = True)
#     authorizer = models.ForeignKey(null = False, to = User, on_delete = models.PROTECT, db_column = 'authorizer_id', related_name = 'groupauthorization_authorizer_id')
    
#     class Meta:
#         unique_together = ('user_id', 'group_privilege_id', 'group_id')
        
#     objects = models.Manager()




# class GroupMembers(models.Model):  -------->    moved to GroupAuthorization
#     group = models.ForeignKey(null = False, to = Group, on_delete = models.CASCADE, db_column = 'group_id', related_name = 'groupmembers_group_id')
#     user = models.ForeignKey(null = False, to = User, on_delete = models.CASCADE, db_column = 'user_id', related_name = 'groupmembers_user_id')
#     created = models.DateTimeField(null = False, auto_now_add = True)
#     inviter = models.ForeignKey(null = False, to = User, on_delete = models.PROTECT, db_column = 'inviter_id', related_name = 'groupmembers_inviter_id')
#     class Meta:
#         unique_together = ('group_id', 'user_id')
#     objects = models.Manager()
