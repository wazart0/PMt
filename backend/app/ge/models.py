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
#     -- dependency_type INTEGER, -- cannot remind why
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
from django.contrib.postgres.fields import JSONField


import libs.GraphEngine.abstract_model as ge





# class NodeModelManager(models.Manager):

#     def create(self, creator_id, *args, **kwargs):
#         # print("Object creation ( type ): \t\t\t( " + str(self.model.node_type) + ' )')
#         if creator_id != None:
#             requester = Node.objects.get(id=creator_id)
#             if requester.node_type.pk != 'user':
#                 raise FieldError("Creator doesn't exists: " + str(creator_id))
#         node = Node.objects.create(node_type=NodeType.objects.get(id=self.model.node_type))
#         if creator_id != None:
#             Node.objects.connect_nodes(requester, node, creator='True')
#         obj = super().create(id=node, *args, **kwargs)
#         # print("Object created ( type | pk | object ): \t\t( " + str(obj.node_type) + " | " + str(obj.pk) + " | " + str(obj.id) + ' )')
#         return obj

#     def get_predecessors(self, node_id, edge_column=None, edge_column_value=None):
#         if edge_column == 'timeline_dependency':
#             return self.filter(id__in=RawSQL(
#                 '''
#                     SELECT n.id FROM ge_node n LEFT JOIN ge_edge e ON n.id = e.source_node_id WHERE e.target_node_id = %s AND n.node_type = %s AND e.timeline_dependency IS NOT NULL
#                 ''', [node_id, self.model.node_type])).order_by('id')
#         return self.filter(id__in=RawSQL(
#             '''
#                 SELECT n.id FROM ge_node n LEFT JOIN ge_edge e ON n.id = e.source_node_id WHERE e.target_node_id = %s AND n.node_type = %s
#             ''', [id, self.model.node_type])).order_by('id')
            
#     def get_successors(self, node_id, edge_column=None, edge_column_value=None):
#         if edge_column == 'timeline_dependency':
#             return self.filter(id__in=RawSQL(
#                 '''
#                     SELECT n.id FROM ge_node n LEFT JOIN ge_edge e ON n.id = e.target_node_id WHERE e.source_node_id = %s AND n.node_type = %s AND e.timeline_dependency IS NOT NULL
#                 ''', [node_id, self.model.node_type])).order_by('id')
#         return self.filter(id__in=RawSQL(
#             '''
#                 SELECT n.id FROM ge_node n LEFT JOIN ge_edge e ON n.id = e.target_node_id WHERE e.source_node_id = %s AND n.node_type = %s
#             ''', [id, self.model.node_type])).order_by('id')



# class GraphModelManager(models.Manager):

#     @staticmethod
#     def connect_nodes(source, target, **kwargs):
#         if source is None or target is None or kwargs is None:
#             raise FieldError('MISSING PARAMETERS: Cannot connect nodes (' + str(source) + ' -> ' + str(target) + '): ' + str(kwargs))
#         edge = Edge.objects.filter(source_node=source, target_node=target)
#         if len(edge) == 0:
#             return Edge.objects.create(source_node=source, target_node=target, **kwargs)
#         edge.update(**kwargs)
#         return edge[0]






# class NodeType(models.Model): # if this required?
#     id = models.CharField(primary_key=True, max_length=30, editable=False, db_column='id')
#     display_name = models.TextField(null=False)
#     description = models.TextField(null=True)

#     objects = models.Manager()


# class Node(models.Model):
#     id = models.BigAutoField(primary_key=True, editable=False, db_column = 'id')

#     # creator = models.ForeignKey('self', models.SET_NULL, null=True, editable=False, db_column='creator', related_name='node_creator')
#     node_type = models.ForeignKey(null=False, to=NodeType, editable=False, db_column='node_type', related_name='node_node_type', on_delete=models.PROTECT)

#     objects = GraphModelManager()


# # TODO make it generic and add materialized views
# class Edge(models.Model): # probably this should be hidden in Node class

#     source_node = models.ForeignKey(to=Node, null=False, editable=False, db_column='source_node_id', related_name='edge_source_node_id', on_delete=models.PROTECT)
#     target_node = models.ForeignKey(to=Node, null=False, editable=False, db_column='target_node_id', related_name='edge_target_node_id', on_delete=models.PROTECT)

#     timeline_dependency = models.CharField(null=True, max_length=2, choices=(
#         ('SS', 'Start-Start'),
#         ('SF', 'Start-Finish'),
#         ('FS', 'Finish-Start'),
#         ('FF', 'Finish-Finish')
#     )) # None | start-start | start-finish | finish-start | finish-finish
#     cost_dependency = models.BooleanField(null=True)
#     resource_dependency = models.BooleanField(null=True)
#     creator = models.BooleanField(null=True)
#     assignee = models.BooleanField(null=True)
#     belongs_to = models.BooleanField(null=True)
#     member = models.BooleanField(null=True) # TODO has to be moved to permission level probably

#     objects = models.Manager()

#     class Meta:
#         unique_together = ('source_node', 'target_node')




class VertexType(models.Model):
    id = models.CharField(primary_key=True, max_length=30, editable=False, db_column='id')

    display_name = models.TextField(null=False)
    description = models.TextField(null=True)


class EdgeType(models.Model):
    id = models.CharField(primary_key=True, max_length=30, editable=False, db_column='id')

    display_name = models.TextField(null=False)
    description = models.TextField(null=True)


class Vertex(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False, db_column = 'id')
    vertex_type = models.ForeignKey(null=False, to=VertexType, editable=False, db_column='vertex_type_id', related_name='vertex_vertex_type_id', on_delete=models.PROTECT)


class Edge(models.Model):
    class Meta:
        unique_together = ('source_vertex', 'target_vertex', 'edge_type')
    source_vertex = models.ForeignKey(to=Vertex, null=False, editable=False, db_column='source_vertex_id', related_name='edge_source_vertex_id', on_delete=models.PROTECT)
    target_vertex = models.ForeignKey(to=Vertex, null=False, editable=False, db_column='target_vertex_id', related_name='edge_target_vertex_id', on_delete=models.PROTECT)
    edge_type = models.ForeignKey(null=False, to=EdgeType, editable=False, db_column='edge_type_id', related_name='edge_edge_type_id', on_delete=models.PROTECT)

    details = JSONField(null=True)




# class VertexAbstractObject(models.Model):
#     class Meta:
#         abstract = True
#     objects = DirectedGraphModelManager()
#     id = models.OneToOneField(to=Vertex, primary_key=True, editable=False, db_column='id', on_delete=models.PROTECT)


class DirectedGraphModelManager(models.Manager):
    # names of tables in db
    vertex_type_table_name = VertexType._meta.db_table
    vertex_table_name = Vertex._meta.db_table
    edge_type_table_name = EdgeType._meta.db_table
    edge_table_name = Edge._meta.db_table

        
    def create(self, creator_id, *args, **kwargs):
        if creator_id != None:
            requester = Vertex.objects.get(id=creator_id)
            if requester.vertex_type.pk != 'user':
                raise FieldError("Creator doesn't exists: " + str(creator_id))
        vertex = Vertex.objects.create(vertex_type=VertexType.objects.get(id=self.model.vertex_type))
        if creator_id != None:
            DirectedGraphModelManager.connect_nodes(requester, vertex, EdgeType.objects.get(id='creator'))
        return super().create(id=vertex, *args, **kwargs)


    def get_predecessors(self, node_id, edge_type_name = None):
        return self.filter(id__in=RawSQL(
            '''
                SELECT id
                FROM {edge_table_name}
                WHERE target_vertex_id = {node_id}
            '''.format(
                edge_table_name = self.edge_table_name,
                node_id = node_id
            ))).order_by('id')


    def get_successors(self, node_id, edge_type_name = None):
        return self.filter(id__in=RawSQL(
            '''
                SELECT id
                FROM {edge_table_name}
                WHERE source_vertex_id = {node_id}
            '''.format(
                edge_table_name = self.edge_table_name,
                node_id = node_id
            ))).order_by('id')


    @staticmethod
    def connect_nodes(source, target, type, **kwargs):
        if source is None or target is None or type is None:
            raise FieldError('MISSING PARAMETERS: Cannot connect nodes (' + str(source) + ' -> ' + str(target) + '): ' + str(kwargs))
        edge = Edge.objects.filter(source_vertex=source, target_vertex=target, edge_type=type)
        if len(edge) == 0:
            return Edge.objects.create(source_vertex=source, target_vertex=target, edge_type=type, **kwargs)
        edge.update(**kwargs)
        return edge[0]
        



