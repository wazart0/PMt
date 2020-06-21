drop table if exists timeline_dependency;

create temp table timeline_dependency as (
	select
		ge_edge.target_vertex_id as project_id,
		ge_edge.source_vertex_id as predecessor_id,
		ge_edge.details->>'type' as dependence
	from
		ge_edge
	where 
		ge_edge.source_vertex_id in (select project_id from projects_in_tree)
	and
		ge_edge.target_vertex_id in (select project_id from projects_in_tree)
	and
		ge_edge.edge_type_id = 'dependence'
);

