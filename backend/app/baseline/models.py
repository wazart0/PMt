from django.db import models

from graph_engine.models import Node, NodeModelManager
import graph_engine.models as ge
from project.models import Project
from ums.models import User



class Baseline(models.Model):
    node_type = 'baseline'
    objects = NodeModelManager()
    id = models.OneToOneField(to=Node, primary_key=True, editable=False, db_column='id', related_name='baseline', on_delete=models.PROTECT)

    created = models.DateTimeField(null=False, editable=False, auto_now_add=True)
    updated = models.DateTimeField(null=False, editable=False, auto_now=True) # TODO special logger has to be implemented - later remove

    name = models.CharField(null=False, max_length=100)
    description = models.TextField(null=True, default=None)
    default = models.BooleanField(default=False)



class Timeline(models.Model):
    # TODO check why Node is required instead of Baseline
    baseline = models.ForeignKey(to=Node, null=False, db_column='baseline', related_name='timeline_baseline', on_delete=models.CASCADE)
    
    project = models.ForeignKey(to=Project, null=False, db_column='project', related_name='timeline_project', on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, null=True, db_column='user', related_name='timeline_user', on_delete=models.CASCADE)
    start = models.DateTimeField(null=False)
    finish = models.DateTimeField(null=False)


class ProjectDependency(models.Model):
    # TODO check why Node is required instead of Baseline
    baseline = models.ForeignKey(to=Node, null=False, db_column='baseline', related_name='projectdependency_baseline', on_delete=models.CASCADE)

    project = models.ForeignKey(to=Project, null=False, db_column='project', related_name='projectdependency_project', on_delete=models.CASCADE)
    predecessor = models.ForeignKey(to=Project, null=False, db_column='predecessor', related_name='projectdependency_predecessor', on_delete=models.CASCADE)
    timeline_dependency = models.CharField(null=True, max_length=2, choices=(
        ('SS', 'Start-Start'),
        ('SF', 'Start-Finish'),
        ('FS', 'Finish-Start'),
        ('FF', 'Finish-Finish')
    )) # None | start-start | start-finish | finish-start | finish-finish


class Project(models.Model):
    # TODO check why Node is required instead of Baseline
    baseline = models.ForeignKey(to=Node, null=False, db_column='baseline', related_name='project_baseline', on_delete=models.CASCADE)
    
    project = models.ForeignKey(to=Project, null=False, db_column='project', related_name='project_project', on_delete=models.CASCADE)
    belongs_to = models.ForeignKey(to=Project, null=False, db_column='belongs_to', related_name='project_belongs_to', on_delete=models.CASCADE)
    worktime_planned = models.DurationField(null=False)
    # user = models.ForeignKey(to=User, null=True, db_column='user', related_name='timeline_user', on_delete=models.CASCADE)
    start = models.DateTimeField(null=False)
    finish = models.DateTimeField(null=False)
    wbs = models.TextField(null=False)

