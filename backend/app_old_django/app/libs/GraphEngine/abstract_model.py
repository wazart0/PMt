from django.db import models, connection
from django.core.exceptions import FieldError
from django.db.models.expressions import RawSQL




class VertexType(models.Model):
    class Meta:
        abstract = True
    id = models.CharField(primary_key=True, max_length=30, editable=False, db_column='id')
    name = models.TextField(null=False, blank=False)


class EdgeType(models.Model):
    class Meta:
        abstract = True
    id = models.CharField(primary_key=True, max_length=30, editable=False, db_column='id')
    name = models.TextField(null=False, blank=False)


class Vertex(models.Model):
    class Meta:
        abstract = True
    id = models.BigAutoField(primary_key=True, editable=False, db_column = 'id')
    vertex_type = models.ForeignKey(null=False, to=VertexType, editable=False, db_column='vertex_type_id', related_name='vertex_vertex_type_id', on_delete=models.PROTECT)


class Edge(models.Model):
    class Meta:
        abstract = True
        unique_together = ('source_node', 'target_node', 'edge_type')
    source_vertex = models.ForeignKey(to=Vertex, null=False, editable=False, db_column='source_vertex_id', related_name='edge_source_vertex_id', on_delete=models.PROTECT)
    target_vertex = models.ForeignKey(to=Vertex, null=False, editable=False, db_column='target_vertex_id', related_name='edge_target_vertex_id', on_delete=models.PROTECT)
    edge_type = models.ForeignKey(null=False, to=EdgeType, editable=False, db_column='edge_type_id', related_name='edge_edge_type_id', on_delete=models.PROTECT)




class DirectedGraphModelManager(models.Manager):
    # names of tables in db
    def __init__(self, vertex_type_table_name, vertex_table_name, edge_type_table_name, edge_table_name):
        self.vertex_type_table_name = vertex_type_table_name
        self.vertex_table_name = vertex_table_name
        self.edge_type_table_name = edge_type_table_name
        self.edge_table_name = edge_table_name
        super().__init__(self)

        
    def create(self, *args, **kwargs):
        node = Vertex.objects.create(node_type=VertexType.objects.get(id=self.model.node_type))
        return super().create(id=node, *args, **kwargs)


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
    def connect_nodes(source, target, **kwargs):
        if source is None or target is None or kwargs is None:
            raise FieldError('MISSING PARAMETERS: Cannot connect nodes (' + str(source) + ' -> ' + str(target) + '): ' + str(kwargs))
        edge = Edge.objects.filter(source_node=source, target_node=target)
        if len(edge) == 0:
            return Edge.objects.create(source_node=source, target_node=target, **kwargs)
        edge.update(**kwargs)
        return edge[0]
        
