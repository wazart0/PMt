from django.db import models

from graph_engine.models import Node, NodeModelManager
import graph_engine.models as ge





class Project(models.Model):
    node_type = 'project'
    objects = NodeModelManager()
    id = models.OneToOneField(to=Node, primary_key=True, editable=False, db_column='id', related_name='project', on_delete=models.PROTECT)

    created = models.DateTimeField(null=False, editable=False, auto_now_add=True)
    updated = models.DateTimeField(null=False, editable=False, auto_now=True) # TODO special logger has to be implemented - later remove

    name = models.CharField(null=False, max_length=100)
    description = models.TextField(null=True, default=None)
    closed = models.DateTimeField(null=True)
    worktime_planned = models.DurationField(null=True) # worktime required -> if none then calulate based on subprojects and operations
    # project_type -> project/task/user story/epic/other

    # responsible user -> it is just a supervisor of given project - not assignee
    def add_assignee(self, user): #  TODO assignee should be managed on resource level
        pass


    # @property
    # def has_belonger_(self):
    #     return True
    #     return len(ge.Edge.objects.filter(target_node=self.pk, belongs_to=True)) != 0
    




class Milestone(models.Model):
    node_type = 'milestone'
    objects = NodeModelManager()
    id = models.OneToOneField(to=Node, primary_key=True, editable=False, db_column='id', related_name='milestone', on_delete=models.PROTECT)

    created = models.DateTimeField(null = False, auto_now_add = True)
    updated = models.DateTimeField(null = False, auto_now = True)

    timestamp = models.DateTimeField(null = False)
    name = models.CharField(null = False, max_length = 50)
    description = models.TextField(null = True)
    color = models.CharField(null = False, max_length = 7)
        
