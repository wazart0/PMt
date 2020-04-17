create temp table projects_in_tree as (
	with recursive
	project_edges as (
		select
			graph_engine_edge.*
		from
			graph_engine_edge 
		inner join
			project_project as source_project
		on 
			source_node_id = source_project.id
		inner join
			project_project as target_project
		on
			target_node_id = target_project.id
	),
	project_hierarchy as (
		select * from project_edges where belongs_to = 'True'
	),
	project_tree as (
		select s1.source_node_id from project_hierarchy as s1 where s1.target_node_id = {top_level_node_id}
		union all
		select s2.source_node_id from project_hierarchy as s2, project_tree as s1 where s2.target_node_id = s1.source_node_id
	)
	select source_node_id as project_id from project_tree
);

create temp table project_edges as (
	select
		*
	from
		graph_engine_edge
	where 
		graph_engine_edge.source_node_id in (select * from projects_in_tree)
	and
		graph_engine_edge.target_node_id in (select * from projects_in_tree)
);

