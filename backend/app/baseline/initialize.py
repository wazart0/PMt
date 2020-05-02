from django.db.models.signals import post_migrate
from django.db import connection
 




def create_views(sender, **kwargs):
    
    query = '''
        drop view if exists baseline_project;
        create view baseline_project as (
            select
                baseline_timeline.baseline,
                baseline_timeline.project,
                min(baseline_timeline.id) as id,
                min(baseline_timeline.start) as start,
                max(baseline_timeline.finish) as finish
            from 
                baseline_timeline
            group by 
                project,
                baseline
        );
    '''

    print('Initializing baseline views...')
    cursor = connection.cursor()
    cursor.execute(query)