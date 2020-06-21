from django.db import models, connection
from django.core.exceptions import FieldError
from django.db.models.expressions import RawSQL




class GraphModelManager(models.Manager):
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


