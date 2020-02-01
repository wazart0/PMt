from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.exceptions import FieldError

from graph_engine.models import Node, NodeType


class User(AbstractBaseUser):
    node_type = 'user'
    id = models.OneToOneField(to=Node, primary_key=True, editable=False, db_column='id', related_name='user_id', on_delete=models.PROTECT)
    # node_type = models.ForeignKey(null=False, to=NodeType, editable=False, db_column='node_type', related_name='user_node_type', on_delete=models.PROTECT)
    # creator_id = models.ForeignKey(null = True, to = 'self', on_delete = models.SET_NULL, db_column = 'creator_id', related_name = 'user_creator_id')
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

    def __init__(self, *args, **kwargs):
        self.creator_id = None
        super().__init__(*args, **kwargs)

    def save(self, force_insert = False, force_update = False, using = None, update_fields = None):
        print("User pk: " + str(self.pk))  # TODO remove later
        # print("User id: " + str(self.id))  # TODO remove later --> now it doesn't exists !!!
        self.creator_id = Node.objects.get(id=3) # TODO refactor to get from access/refresh tokens
        if self.pk == None:
            # create node
            self.id = Node.objects.create(node_type=NodeType.objects.get(id=self.node_type))
            super().save(force_insert, force_update, using, update_fields)
            print('creator id: ' + str(self.creator_id))
            if self.creator_id != None:
                Node.objects.connect_nodes(self.creator_id, self.id, creator='True')
        else:
            super().save(force_insert, force_update, using, update_fields)
        print("User pk: " + str(self.pk))  # TODO remove later
        print("User id: " + str(self.id))  # TODO remove later
        return self
    



class Group(models.Model):
    creator_id = models.ForeignKey(null = False, to = User, on_delete = models.PROTECT, db_column = 'creator_id', related_name = 'group_creator_id')
    created = models.DateTimeField(null = False, editable = False, auto_now_add = True)
    updated = models.DateTimeField(null = False, editable = False, auto_now = True)

    name = models.CharField(null = False, max_length = 50)
    description = models.TextField(null = True, default = None)
    parent_id = models.ForeignKey(null = True, to = 'self', on_delete = models.CASCADE, db_column = 'parent_id', related_name = 'group_parent_id')
    is_active = models.BooleanField(null = False, default = True)
    is_hidden = models.BooleanField(null = False, editable = False, default = False)

    objects = models.Manager()

    # TODO improve protection against creator_id modification (editable = False - prevents possibility of instance creation)
    def save(self, force_insert = False, force_update = False, using = None, update_fields = None): 
        isCreated = True
        if self.pk is not None:
            isCreated = False

        models.Model.save(self, force_insert, force_update, using, update_fields)
        if (isCreated == True and self.pk is not None) or force_insert == True:
            groupPrivileges = GroupPrivileges.objects.all()
            for privilege in groupPrivileges:
                GroupAuthorization.objects.create(user_id = self.creator_id, group_privilege_id = privilege, group_id = self, authorizer_id = self.creator_id)



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




# class GroupMembers(models.Model):  -------->    moved to GroupAuthorization
#     group_id = models.ForeignKey(null = False, to = Group, on_delete = models.CASCADE, db_column = 'group_id', related_name = 'groupmembers_group_id')
#     user_id = models.ForeignKey(null = False, to = User, on_delete = models.CASCADE, db_column = 'user_id', related_name = 'groupmembers_user_id')
#     created = models.DateTimeField(null = False, auto_now_add = True)
#     inviter_id = models.ForeignKey(null = False, to = User, on_delete = models.PROTECT, db_column = 'inviter_id', related_name = 'groupmembers_inviter_id')
#     class Meta:
#         unique_together = ('group_id', 'user_id')
#     objects = models.Manager()
