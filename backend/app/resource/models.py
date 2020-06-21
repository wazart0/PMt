from django.db import models

from ge.models import Node, NodeModelManager





class TimeResource(models.Model):
    vertex_type = 'timeresource'
    objects = NodeModelManager()
    id = models.OneToOneField(to=Node, primary_key=True, editable=False, db_column='id', related_name='timeresource_id', on_delete=models.PROTECT)

    created = models.DateTimeField(null = False, editable = False, auto_now_add = True)
    updated = models.DateTimeField(null = False, editable = False, auto_now = True) # TODO special logger has to be implemented - later remove

    # name = models.CharField(null = False, max_length = 100)
    # time_resource = models.BooleanField(null=True) # TODO think about
    # availability 8h/day, 32h/day, 168h/month -> to be refought (probably float)
    resource_type = models.CharField(null=True, max_length=10, choices=(
        ('human', 'Human resource'),
        ('company', 'Company resource'),
    ))

