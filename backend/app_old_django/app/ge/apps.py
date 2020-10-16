from django.apps import AppConfig
from django.db.models.signals import post_migrate

from ge.initialize import vertex_type_init, edge_type_init



class GraphEngineConfig(AppConfig):
    name = 'ge'

    def ready(self):
        post_migrate.connect(vertex_type_init, sender=self)
        post_migrate.connect(edge_type_init, sender=self)
