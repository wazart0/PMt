create temp table lowest_level_projects as (
	with
	owns as (
		select 
			target_vertex_id as project_id, 
			source_vertex_id as own_id 
		from 
			project_edges 
		where 
			edge_type_id = 'belongs_to'
	)
	select
		id as project_id,
		worktime_planned
	from
		project_project
	where
		id not in (select project_id from owns)
	and
		id in (select project_id from projects_in_tree)
);
