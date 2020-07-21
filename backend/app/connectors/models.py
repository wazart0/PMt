from django.db import models

from ge.models import Vertex, DirectedGraphModelManager
import ge.models as ge

# Create your models here.




class JiraAuth(models.Model):
    vertex_type = 'jira_auth'
    objects = DirectedGraphModelManager()
    id = models.OneToOneField(to=Vertex, primary_key=True, editable=False, db_column='id', related_name='jira_id', on_delete=models.PROTECT)

    # jql = models.TextField(null=False)
    url = models.URLField(null=False)
    login = models.CharField(null=False, max_length=30)
    auth_key = models.CharField(null=False, max_length=30)
    




class GanttProject(models.Model):
    pass


