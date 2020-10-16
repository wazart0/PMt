from django.db import models

from ge.models import Vertex, DirectedGraphModelManager
import ge.models as ge





class Availability(models.Model):
    vertex_type = 'availability'
    objects = DirectedGraphModelManager()
    id = models.OneToOneField(to=Vertex, primary_key=True, editable=False, db_column='id', related_name='availability_id', on_delete=models.PROTECT)

    created = models.DateTimeField(null=False, editable=False, auto_now_add=True)
    updated = models.DateTimeField(null=False, editable=False, auto_now=True) # TODO special logger has to be implemented - later remove

    start = models.DateTimeField(null=False)
    finish = models.DateTimeField(null=True) 

    duration = models.DurationField(null=True) # if partially available in given interval
    repeat_interval = models.DurationField(null=True) # if partially available in given interval

    # TODO add constraints: (duration < repeat_interval)

