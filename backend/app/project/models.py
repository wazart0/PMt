from django.db import models

from graph_engine.models import Node, NodeModelManager
import graph_engine.models as ge



# class Status(models.Model):
#     name = models.CharField(null = False, max_length = 50)
#     description = models.TextField(null = True)
#     trigger = models.CharField(null = True, default = None, max_length = 1,
#                             choices = (
#                                 ('e', "execute"), # sets start execution while setting this status, sets stop execution while leaving
#                                 ('t', "executeAndLogTime"), # as above + requires logging time while leaving status or change assignee
#                                 ('c', "close") # sets close status
#                             ))
#     # TODO some icons, etc

#     objects = models.Manager()

# class Type(models.Model):
#     name = models.CharField(null = False, max_length = 50)
#     description = models.TextField(null = True)
#     color = models.CharField(null = False, max_length = 7)

#     objects = models.Manager()

# class TypeStatuses(models.Model):
#     type_id = models.ForeignKey(null = False, to = Type, on_delete = models.CASCADE, db_column = 'type_id')
#     status_id = models.ForeignKey(null = False, to = Status, on_delete = models.CASCADE, db_column = 'status_id')
#     class Meta:
#         unique_together = ('type_id', 'status_id')
        
#     objects = models.Manager()



class Project(models.Model):
    node_type = 'project'
    objects = NodeModelManager()
    id = models.OneToOneField(to=Node, primary_key=True, editable=False, db_column='id', related_name='project_id', on_delete=models.PROTECT)

    created = models.DateTimeField(null=False, editable=False, auto_now_add=True)
    updated = models.DateTimeField(null=False, editable=False, auto_now=True) # TODO special logger has to be implemented - later remove

    name = models.CharField(null=False, max_length=100)
    description = models.TextField(null=True, default=None)
    worktime_planned = models.DurationField(null=True) # worktime required -> if none then calulate based on subprojects and operations
    # project_type -> project/task/user story/epic/other
    # project_state -> we should differentiate 3 basic states: [pending, executing, completed]
    start = models.DateTimeField(null=True)
    finish = models.DateTimeField(null=True)

    # responsible user -> it is just a supervisor of given project - not assignee
    def add_assignee(self, user_id): #  TODO assignee should be managed on resource level
        pass


    # @property
    # def has_belonger_(self):
    #     return True
    #     return len(ge.Edge.objects.filter(target_node_id=self.pk, belongs_to=True)) != 0
        


# class ProjectState(models.Model):
#     project_id = models.ForeignKey(to=Project, editable=False, db_column='project_id', related_name='projectstate_project_id', on_delete=models.CASCADE)
#     timestamp = models.DateTimeField(null = False)
#     state = models.CharField(null=False, max_length=1, choices=(
#         ('e', "execution"),
#         ('p', "pending"),
#         ('c', "completed")
#     ))



class Milestone(models.Model):
    node_type = 'milestone'
    objects = NodeModelManager() # TODO should it really have ID not project-dependent?
    id = models.OneToOneField(to=Node, primary_key=True, editable=False, db_column='id', related_name='milestone_id', on_delete=models.PROTECT)

    created = models.DateTimeField(null = False, auto_now_add = True)
    updated = models.DateTimeField(null = False, auto_now = True)

    timestamp = models.DateTimeField(null = False)
    name = models.CharField(null = False, max_length = 50)
    description = models.TextField(null = True)
    color = models.CharField(null = False, max_length = 7)




