from django.db import models

from graph_engine.models import Node, NodeModelManager
import graph_engine.models as ge
from project.models import Project
from ums.models import User
# from baseline.models import bl





class Project(models.Model): # TODO deprecated for some time only
    class Meta:
        managed = False
        db_table = 'baseline_project'

    baseline = models.ForeignKey(to=Node, null=False, db_column='baseline', related_name='timeline_baseline', on_delete=models.CASCADE)
    
    project = models.ForeignKey(to=Project, null=False, db_column='project', related_name='timeline_project', on_delete=models.CASCADE)
    # user = models.ForeignKey(to=User, null=True, db_column='user', related_name='timeline_user', on_delete=models.CASCADE)
    start = models.DateTimeField(null=False)
    finish = models.DateTimeField(null=False)
    # wbs = models.TextField(null=False) # TODO implement, include initialize

