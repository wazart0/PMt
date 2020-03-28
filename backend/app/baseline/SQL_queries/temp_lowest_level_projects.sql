create temp table lowest_level_projects as (
	with
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
	owns as (
		select 
			target_node_id as project_id, 
			source_node_id as own_id 
		from 
			project_edges 
		where 
			belongs_to = 'True'
	)
	select
		id as project_id,
		worktime_planned
	from
		project_project
	where
		id not in (select project_id from owns)
);
