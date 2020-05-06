drop table if exists timeline_dependency;

create temp table timeline_dependency as (
	select
		graph_engine_edge.target_node_id as project_id,
		graph_engine_edge.source_node_id as predecessor_id,
		graph_engine_edge.timeline_dependency as dependence
	from
		graph_engine_edge
	where 
		graph_engine_edge.source_node_id in (select project_id from projects_in_tree)
	and
		graph_engine_edge.target_node_id in (select project_id from projects_in_tree)
	and
		graph_engine_edge.timeline_dependency is not null
);

