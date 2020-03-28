from django.db.models.signals import post_migrate
from django.db import connection
 




def node_type_init(sender, **kwargs):
    
    query = '''
    INSERT INTO graph_engine_nodetype
        (id, display_name, description)
    SELECT %s, %s, %s
    WHERE
        NOT EXISTS (
            SELECT id FROM graph_engine_nodetype WHERE id = %s
        );
    '''

    data = [
        ['user', 'User', None, 'user'],
        ['group', 'Group', None, 'group'],
        ['project', 'Project', '“A project is a temporary organization that is created for the purpose of delivering one or more business products according to an agreed Business Case.”', 'project'],
        ['operation', 'Operation', 'Operations are the ongoing execution of activities and they follow an organization’s procedures to produce the same result or a repetitive service. Operations are permanent in nature.', 'operation'],
        ['availability', 'Availability', None, 'availability']
    ]

    print('Initializing node types...')
    cursor = connection.cursor()
    for i in data:
        cursor.execute(query, i)
