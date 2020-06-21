from django.db.models.signals import post_migrate
from django.db import connection
 




def vertex_type_init(sender, **kwargs):
    
    query = '''
    INSERT INTO ge_vertextype
        (id, display_name, description)
    SELECT %s, %s, %s
    WHERE
        NOT EXISTS (
            SELECT id FROM ge_vertextype WHERE id = %s
        );
    '''

    data = [
        ['user', 'User', None, 'user'],
        ['group', 'Group', None, 'group'],
        ['project', 'Project', '“A project is a temporary organization that is created for the purpose of delivering one or more business products according to an agreed Business Case.”', 'project'],
        ['operation', 'Operation', 'Operations are the ongoing execution of activities and they follow an organization’s procedures to produce the same result or a repetitive service. Operations are permanent in nature.', 'operation'],
        ['availability', 'Availability', None, 'availability'],
        ['baseline', 'Baseline', None, 'baseline']
    ]

    print('Initializing vertex types...')
    cursor = connection.cursor()
    for i in data:
        cursor.execute(query, i)


def edge_type_init(sender, **kwargs):
    
    query = '''
    INSERT INTO ge_edgetype
        (id, display_name, description)
    SELECT %s, %s, %s
    WHERE
        NOT EXISTS (
            SELECT id FROM ge_edgetype WHERE id = %s
        );
    '''

    data = [
        ['creator', 'Creator', None, 'creator'],
        ['calendar', 'Calendar', None, 'calendar'],
        ['dependence', 'Dependency', None, 'dependence'],
        ['belongs_to', 'Belongs to', None, 'belongs_to']
    ]

    print('Initializing edge types...')
    cursor = connection.cursor()
    for i in data:
        cursor.execute(query, i)