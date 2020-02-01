# -- Directional hypergraph engine implementation
# -- https://www.slideshare.net/quipo/rdbms-in-the-social-networks-age/36-Nodes_and_Edges_nodesCREATE_TABLE
# -- Caching ideas:
# --  * check if edges table changed if not then use nodes from cache (do not search again)



# CREATE TABLE nodes (
#     id SERIAL PRIMARY KEY,
#     -- Custom fields:
#     node_type INTEGER
# );

# CREATE TABLE edges (
#     source_node INTEGER NOT NULL REFERENCES nodes(id) ON UPDATE CASCADE ON DELETE CASCADE,
#     target_node INTEGER NOT NULL REFERENCES nodes(id) ON UPDATE CASCADE ON DELETE CASCADE,
#     PRIMARY KEY (source_node, target_node),
#     -- Custom fields:
#     -- hierarchy BOOLEAN, -- if this required?
#     -- dependancy_type INTEGER, -- cannot remind why
#     -- privileges_dependency BOOLEAN, -- can't remind why
#     cost_dependency BOOLEAN,
#     time_dependency BOOLEAN,
#     resource_dependency BOOLEAN
# );

# ALTER TABLE edges ADD CONSTRAINT no_self_loops CHECK (source_node <> target_node);

# SELECT * FROM edges WHERE source_node = 2;


# interesting notes: https://adamj.eu/tech/2019/08/07/how-to-add-database-modifications-beyond-migrations-to-your-django-project/

from django.db import models, connection
from django.core.exceptions import FieldError



class NodeType(models.Model): # if this required?
    id = models.CharField(primary_key=True, max_length=20, editable=False, db_column='id')
    display_name = models.TextField(null=False)
    description = models.TextField(null=True)

    objects = models.Manager()

# class TimeDependency(models.Model): # if this required?
#     pass


class GraphModelManager(models.Manager):
    class QuerySet(models.QuerySet):
        def get_closest_nodes(self):
            return self.filter(id__in=RawSQL(
                '''
                    SELECT id FROM node n LEFT JOIN edge e ON n.id = e.b WHERE e.a = %s
                ''', id)).order_by('id')
        
    def get_queryset(self):
        return self.QuerySet(self.model, using=self.db)

    @staticmethod
    def connect_nodes(source, target, **kwargs):
        if source is None or target is None or kwargs is None:
            raise FieldError('MISSING PARAMETERS: Cannot connect nodes (' + str(source) + ' -> ' + str(target) + '): ' + str(kwargs))
        return Edge.objects.create(source_node_id=source, target_node_id=target, **kwargs)
        # cursor = connection.cursor()
        # string = ''
        # for i in list(kwargs.keys()):
        #     string += i
        # cursor.execute(
        #     '''
        #         INSERT INTO graph_engine_edge (source_node_id, target_node_id, {fields}) 
        #         VALUES (%s, %s, %s)
        #     ''')
        # print(str(source) + ' -> ' + str(target))
        # print(kwargs)
        # print(bool(kwargs))
        # print('\n')



class Node(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False, db_column = 'id')

    node_type = models.ForeignKey(null=False, to=NodeType, editable=False, db_column='node_type', related_name='node_node_type', on_delete=models.PROTECT)

    objects = GraphModelManager()



class Edge(models.Model): # probably this should be hidden in Node class
    class Meta:
        unique_together = ('source_node_id', 'target_node_id')

    source_node_id = models.ForeignKey(to=Node, null=False, editable=False, db_column='source_node_id', related_name='edge_source_node_id', on_delete=models.PROTECT)
    target_node_id = models.ForeignKey(to=Node, null=False, editable=False, db_column='target_node_id', related_name='edge_target_node_id', on_delete=models.PROTECT)

    timeline_dependency = models.CharField(null=True, max_length=2, choices=(
        ('ss', 'Start-Start'),
        ('sf', 'Start-Finish'),
        ('fs', 'Finish-Start'),
        ('ff', 'Finish-Finish')
    )) # None | start-start | start-finish | finish-start | finish-finish
    cost_dependency = models.BooleanField(null=True)
    resource_dependency = models.BooleanField(null=True)
    creator = models.BooleanField(null=True)

    objects = models.Manager()
