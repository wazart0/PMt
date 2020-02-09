from django.db import models

from graph_engine.models import Node, NodeModelManager





class Project(models.Model):
    node_type = 'project'
    objects = NodeModelManager()
    id = models.OneToOneField(to=Node, primary_key=True, editable=False, db_column='id', related_name='project_id', on_delete=models.PROTECT)

    created = models.DateTimeField(null = False, editable = False, auto_now_add = True)
    updated = models.DateTimeField(null = False, editable = False, auto_now = True) # TODO special logger has to be implemented - later remove

    name = models.CharField(null = False, max_length = 100)
    description = models.TextField(null = True, default = None)
    closed = models.DateTimeField(null = True)
    # project_type -> project/task/user story/epic/other

    def add_assignee(self, user_id):
        pass
    





class Milestone(models.Model):
    node_type = 'milestone'
    objects = NodeModelManager()
    id = models.OneToOneField(to=Node, primary_key=True, editable=False, db_column='id', related_name='milestone_id', on_delete=models.PROTECT)

    created = models.DateTimeField(null = False, auto_now_add = True)
    updated = models.DateTimeField(null = False, auto_now = True)

    timestamp = models.DateTimeField(null = False)
    name = models.CharField(null = False, max_length = 50)
    description = models.TextField(null = True)
    color = models.CharField(null = False, max_length = 7)
        
