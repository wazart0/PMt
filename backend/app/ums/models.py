from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser

from graph_engine.models import Node, NodeModelManager



class User(AbstractBaseUser):
    node_type = 'user'
    objects = NodeModelManager()
    id = models.OneToOneField(to=Node, primary_key=True, editable=False, db_column='id', related_name='user', on_delete=models.PROTECT)

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
    id = models.OneToOneField(to=Node, primary_key=True, editable=False, db_column='id', related_name='group', on_delete=models.PROTECT)

    created = models.DateTimeField(null = False, editable = False, auto_now_add = True)
    updated = models.DateTimeField(null = False, editable = False, auto_now = True) # TODO special logger has to be implemented - later remove

    name = models.CharField(null = False, max_length = 50)
    description = models.TextField(null = True, default = None)
    is_active = models.BooleanField(null = False, default = True)
    # group_type -> group | team | organization

    def add_member(self, user):
        user = User.objects.get(id=user)
        Node.objects.connect_nodes(self.id, user.id, member=True)
        return self


    # TODO improve protection against creator modification (editable = False - prevents possibility of instance creation)
    # def save(self, force_insert = False, force_update = False, using = None, update_fields = None): 
    #     isCreated = True
    #     if self.pk is not None:
    #         isCreated = False
    #     models.Model.save(self, force_insert, force_update, using, update_fields)
    #     if (isCreated == True and self.pk is not None) or force_insert == True:
    #         groupPrivileges = GroupPrivileges.objects.all()
    #         for privilege in groupPrivileges:
    #             GroupAuthorization.objects.create(user = self.creator, group_privilege = privilege, group = self, authorizer = self.creator)



# class GroupPrivileges(models.Model): # view, edit: name, add user, remove user, description, active/inactive, change childs parent, manage user privilege
#     name = models.CharField(null = False, max_length = 50)
#     code_name = models.CharField(null = False, max_length = 50, unique = True)
        
#     objects = models.Manager()



# class GroupAuthorization(models.Model):
#     user = models.ForeignKey(null = False, to = User, on_delete = models.CASCADE, db_column = 'user', related_name = 'groupauthorization_user')
#     group_privilege = models.ForeignKey(null = False, to = GroupPrivileges, on_delete = models.CASCADE, db_column = 'group_privilege', related_name = 'groupauthorization_group_privilege')
#     group = models.ForeignKey(null = False, to = Group, on_delete = models.CASCADE, db_column = 'group', related_name = 'groupauthorization_group')
#     created = models.DateTimeField(null = False, editable = False, auto_now_add = True)
#     authorizer = models.ForeignKey(null = False, to = User, on_delete = models.PROTECT, db_column = 'authorizer', related_name = 'groupauthorization_authorizer')
    
#     class Meta:
#         unique_together = ('user', 'group_privilege', 'group')
        
#     objects = models.Manager()




# class GroupMembers(models.Model):  -------->    moved to GroupAuthorization
#     group = models.ForeignKey(null = False, to = Group, on_delete = models.CASCADE, db_column = 'group', related_name = 'groupmembers_group')
#     user = models.ForeignKey(null = False, to = User, on_delete = models.CASCADE, db_column = 'user', related_name = 'groupmembers_user')
#     created = models.DateTimeField(null = False, auto_now_add = True)
#     inviter = models.ForeignKey(null = False, to = User, on_delete = models.PROTECT, db_column = 'inviter', related_name = 'groupmembers_inviter')
#     class Meta:
#         unique_together = ('group', 'user')
#     objects = models.Manager()
