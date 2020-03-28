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
from django.db.models.expressions import RawSQL





class NodeModelManager(models.Manager):    

    def create(self, creator_id, *args, **kwargs):
        # print("Object creation ( type ): \t\t\t( " + str(self.model.node_type) + ' )')
        if creator_id != None:
            requester = Node.objects.get(id=creator_id)
            if requester.node_type.pk != 'user':
                raise FieldError("Creator doesn't exists: " + str(creator_id))
        node = Node.objects.create(node_type=NodeType.objects.get(id=self.model.node_type))
        if creator_id != None:
            Node.objects.connect_nodes(requester, node, creator='True')
        obj = super().create(id=node, *args, **kwargs)
        # print("Object created ( type | pk | object ): \t\t( " + str(obj.node_type) + " | " + str(obj.pk) + " | " + str(obj.id) + ' )')
        return obj

    def get_predecessors(self, node_id, edge_column=None, edge_column_value=None):
        if edge_column == 'timeline_dependancy':
            return self.filter(id__in=RawSQL(
                '''
                    SELECT n.id FROM graph_engine_node n LEFT JOIN graph_engine_edge e ON n.id = e.source_node_id WHERE e.target_node_id = %s AND n.node_type = %s AND e.timeline_dependancy IS NOT NULL
                ''', [node_id, self.model.node_type])).order_by('id')
        return self.filter(id__in=RawSQL(
            '''
                SELECT n.id FROM graph_engine_node n LEFT JOIN graph_engine_edge e ON n.id = e.source_node_id WHERE e.target_node_id = %s AND n.node_type = %s
            ''', [id, self.model.node_type])).order_by('id')
            
    def get_successors(self, node_id, edge_column=None, edge_column_value=None):
        if edge_column == 'timeline_dependancy':
            return self.filter(id__in=RawSQL(
                '''
                    SELECT n.id FROM graph_engine_node n LEFT JOIN graph_engine_edge e ON n.id = e.target_node_id WHERE e.source_node_id = %s AND n.node_type = %s AND e.timeline_dependancy IS NOT NULL
                ''', [node_id, self.model.node_type])).order_by('id')
        return self.filter(id__in=RawSQL(
            '''
                SELECT n.id FROM graph_engine_node n LEFT JOIN graph_engine_edge e ON n.id = e.target_node_id WHERE e.source_node_id = %s AND n.node_type = %s
            ''', [id, self.model.node_type])).order_by('id')



class GraphModelManager(models.Manager):

    @staticmethod
    def connect_nodes(source, target, **kwargs):
        if source is None or target is None or kwargs is None:
            raise FieldError('MISSING PARAMETERS: Cannot connect nodes (' + str(source) + ' -> ' + str(target) + '): ' + str(kwargs))
        return Edge.objects.create(source_node_id=source, target_node_id=target, **kwargs)






class NodeType(models.Model): # if this required?
    id = models.CharField(primary_key=True, max_length=30, editable=False, db_column='id')
    display_name = models.TextField(null=False)
    description = models.TextField(null=True)

    objects = models.Manager()


class Node(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False, db_column = 'id')

    # creator = models.ForeignKey('self', models.SET_NULL, null=True, editable=False, db_column='creator', related_name='node_creator')
    node_type = models.ForeignKey(null=False, to=NodeType, editable=False, db_column='node_type', related_name='node_node_type', on_delete=models.PROTECT)

    objects = GraphModelManager()


class Edge(models.Model): # probably this should be hidden in Node class
    class Meta:
        unique_together = ('source_node_id', 'target_node_id')

    source_node_id = models.ForeignKey(to=Node, null=False, editable=False, db_column='source_node_id', related_name='edge_source_node_id', on_delete=models.PROTECT)
    target_node_id = models.ForeignKey(to=Node, null=False, editable=False, db_column='target_node_id', related_name='edge_target_node_id', on_delete=models.PROTECT)

    timeline_dependancy = models.CharField(null=True, max_length=2, choices=(
        ('SS', 'Start-Start'),
        ('SF', 'Start-Finish'),
        ('FS', 'Finish-Start'),
        ('FF', 'Finish-Finish')
    )) # None | start-start | start-finish | finish-start | finish-finish
    cost_dependency = models.BooleanField(null=True)
    resource_dependency = models.BooleanField(null=True)
    creator = models.BooleanField(null=True)
    assignee = models.BooleanField(null=True)
    belongs_to = models.BooleanField(null=True)
    member = models.BooleanField(null=True) # TODO has to be moved to permission level probably

    objects = models.Manager()
