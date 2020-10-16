from django.apps import AppConfig
from django.db.models.signals import post_migrate

from baseline.initialize import create_views



class BaselineConfig(AppConfig):
    name = 'baseline'

    # def ready(self):
    #     post_migrate.connect(create_views, sender=self)
