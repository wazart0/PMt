from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.db import connection



def node_type_init(sender, **kwargs):
    
    query = '''
        INSERT INTO graph_engine_nodetype
            (id, display_name, description)
        SELECT '{id}', %s, %s
        WHERE
            NOT EXISTS (
                SELECT id FROM graph_engine_nodetype WHERE id = '{id}'
            );
    '''

    data = [
        ['user', 'User', None]
    ]

    print('Initialize node types...')
    cursor = connection.cursor()
    for i in data:
        cursor.execute(query.format(id=i[0]), [i[1], i[2]])


class GraphEngineConfig(AppConfig):
    name = 'graph_engine'

    def ready(self):
        post_migrate.connect(node_type_init, sender=self)
