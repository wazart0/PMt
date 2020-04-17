create temp table lowest_level_projects as (
	with
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
	and
		id in (select * from projects_in_tree)
);
