from django.apps import AppConfig
from django.db.models.signals import post_migrate

from graph_engine.initialize import node_type_init



class GraphEngineConfig(AppConfig):
    name = 'graph_engine'

    def ready(self):
        post_migrate.connect(node_type_init, sender=self)
