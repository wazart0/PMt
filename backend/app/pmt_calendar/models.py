from django.db import models

from graph_engine.models import Node, NodeModelManager
import graph_engine.models as ge





class Availability(models.Model):
    node_type = 'availability'
    objects = NodeModelManager()
    id = models.OneToOneField(to=Node, primary_key=True, editable=False, db_column='id', related_name='availability_id', on_delete=models.PROTECT)

    created = models.DateTimeField(null=False, editable=False, auto_now_add=True)
    updated = models.DateTimeField(null=False, editable=False, auto_now=True) # TODO special logger has to be implemented - later remove

    start = models.DateTimeField(null=False)
    end = models.DateTimeField(null=False)
    repeat_interval = models.DurationField(null=True)
    until = models.DateTimeField(null=True)


