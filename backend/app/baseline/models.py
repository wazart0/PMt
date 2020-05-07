from django.db import models

from graph_engine.models import Node, NodeModelManager
import graph_engine.models as ge
import project.models as pjt
from ums.models import User



class Baseline(models.Model):
    node_type = 'baseline'
    objects = NodeModelManager()
    id = models.OneToOneField(to=Node, primary_key=True, editable=False, db_column='id', related_name='baseline_id', on_delete=models.PROTECT)

    created = models.DateTimeField(null=False, editable=False, auto_now_add=True)
    updated = models.DateTimeField(null=False, editable=False, auto_now=True) # TODO special logger has to be implemented - later remove

    name = models.CharField(null=False, max_length=100)
    description = models.TextField(null=True, default=None)
    default = models.BooleanField(default=False)
    start = models.DateTimeField(null=False, auto_now_add=True)
    # finish should be calculated based on estimations



class Timeline(models.Model): # fragmented timelines
    # TODO check why Node is required instead of Baseline
    baseline = models.ForeignKey(to=Node, null=False, db_column='baseline_id', related_name='timeline_baseline_id', on_delete=models.CASCADE)
    
    project = models.ForeignKey(to=pjt.Project, null=False, db_column='project_id', related_name='timeline_project_id', on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, null=True, db_column='user_id', related_name='timeline_user_id', on_delete=models.CASCADE)
    
    start = models.DateTimeField(null=False)
    finish = models.DateTimeField(null=False)


class ProjectDependency(models.Model):
    # TODO check why Node is required instead of Baseline
    baseline = models.ForeignKey(to=Node, null=False, db_column='baseline_id', related_name='projectdependency_baseline_id', on_delete=models.CASCADE)

    project = models.ForeignKey(to=pjt.Project, null=False, db_column='project_id', related_name='projectdependency_project_id', on_delete=models.CASCADE)
    predecessor = models.ForeignKey(to=pjt.Project, null=False, db_column='predecessor_id', related_name='projectdependency_predecessor_id', on_delete=models.CASCADE)

    timeline_dependency = models.CharField(null=True, max_length=2, choices=(
        ('SS', 'Start-Start'),
        ('SF', 'Start-Finish'),
        ('FS', 'Finish-Start'),
        ('FF', 'Finish-Finish')
    )) # None | start-start | start-finish | finish-start | finish-finish
    llp = models.BooleanField(null=False)


class Project(models.Model):
    # TODO check why Node is required instead of Baseline
    baseline = models.ForeignKey(to=Node, null=False, db_column='baseline_id', related_name='project_baseline_id', on_delete=models.CASCADE)
    
    project = models.ForeignKey(to=pjt.Project, null=False, db_column='project_id', related_name='project_project_id', on_delete=models.CASCADE)
    belongs_to = models.ForeignKey(to=pjt.Project, null=False, db_column='belongs_to', related_name='project_belongs_to', on_delete=models.CASCADE)

    worktime_planned = models.DurationField(null=False)
    start = models.DateTimeField(null=False)    # calculated based on min(Timeline) - to be rethougth to remove and calculate in fly
    finish = models.DateTimeField(null=False)   # calculated based on max(Timeline) - to be rethougth to remove and calculate in fly

    wbs = models.TextField(null=False)
    llp = models.BooleanField(null=False)

