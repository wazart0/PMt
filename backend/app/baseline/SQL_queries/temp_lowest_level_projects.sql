create temp table lowest_level_projects as (
	with
	owns as (
		select 
			target_node as project, 
			source_node as own 
		from 
			project_edges 
		where 
			belongs_to = 'True'
	)
	select
		id as project,
		worktime_planned
	from
		project_project
	where
		id not in (select project from owns)
	and
		id in (select project from projects_in_tree)
);
