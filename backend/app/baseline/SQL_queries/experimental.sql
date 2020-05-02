drop table lowest_level_dependency;
drop table lowest_level_projects;
drop table availability;

create temp table lowest_level_dependency as (
	with
	project_edges as (
		select
			graph_engine_edge.*
		from
			graph_engine_edge 
		inner join
			project_project as source_project
		on 
			source_node = source_project.id
		inner join
			project_project as target_project
		on
			target_node = target_project.id
	),
	owns as (
		select 
			target_node as project, 
			source_node as own 
		from 
			project_edges 
		where 
			belongs_to = 'True'
	),
	lowest_level_dependence as (
		with
		unfiltered_dependency as (
			with recursive 
			dependence_edge as (
				select 
					project_edges.target_node as project,
					project_edges.source_node as predecessor,
					project_edges.timeline_dependency as dependence
				from 
					project_edges
				where
					timeline_dependency is not null
			),
			populate_project as (
					select 
						translation_project.project,
						own.own
					from dependence_edge as translation_project
					join owns as own
					on own.project = translation_project.project
				union 
					select 
						populate_project.project,
						own1.own
					from populate_project
					join owns as own1
					on own1.project = populate_project.own
			),
			populate_predecessors as (
					select 
						translation_predecessor.predecessor,
						own.own
					from dependence_edge as translation_predecessor
					join owns as own
					on own.project = translation_predecessor.predecessor
				union 
					select 
						populate_predecessors.predecessor,
						own1.own
					from populate_predecessors
					join owns as own1
					on own1.project = populate_predecessors.own
			)
			select 
				coalesce (populate_project.own, dependence_edge.project) as project,
				coalesce (populate_predecessors.own, dependence_edge.predecessor) as predecessor,
				dependence_edge.dependence as dependence
			from dependence_edge
			left join populate_project on dependence_edge.project = populate_project.project
			left join populate_predecessors on dependence_edge.predecessor = populate_predecessors.predecessor
		)
		select * 
		from unfiltered_dependency
		where 
			unfiltered_dependency.project not in (select project from owns)
		and
			unfiltered_dependency.predecessor not in (select project from owns)
	)
	select * from lowest_level_dependence
);

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
			source_node = source_project.id
		inner join
			project_project as target_project
		on
			target_node = target_project.id
	),
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
);

alter table lowest_level_projects 
add column timestamp_start timestamptz,
add column timestamp_finish timestamptz;

create temp table availability as (
	with
	basic_availability as (
		select 
			id,
			generate_series(pmt_calendar_availability.start, timestamptz '2020-03-01', pmt_calendar_availability.repeat_interval) as start,
			generate_series(pmt_calendar_availability.finish, timestamptz '2020-03-01', pmt_calendar_availability.repeat_interval) as finish
		from
			pmt_calendar_availability
	)
	select * from basic_availability 
	where start > timestamptz '2020-02-01'
	order by start asc
);


create temp table updated_timestamp as (
	select
		lowest_level_dependency.project as project,
		max(predecessor.timestamp_start + predecessor.worktime_planned) as predecessor_timestamp_finish,
		min(project.timestamp_start) as project_timestamp_start
	from
		lowest_level_dependency
	join lowest_level_projects as predecessor on lowest_level_dependency.predecessor = predecessor.project
	join lowest_level_projects as project on lowest_level_dependency.project = project.project
	where
		lowest_level_dependency.dependence = 'FS'
	group by 
		lowest_level_dependency.project
	having
		min(project.timestamp_start) < max(predecessor.timestamp_start + predecessor.worktime_planned)
);


select * from lowest_level_projects





-- do $$
-- declare 
-- 	row_counter integer := 1;
-- start
-- 	while row_counter > 0 loop
-- 	-- 	with
-- 		create temp table updated_timestamp as (
-- 			select
-- 				lowest_level_dependency.project as project,
-- 				max(predecessor.timestamp_start + predecessor.worktime_planned) as predecessor_timestamp_finish,
-- 				min(project.timestamp_start) as project_timestamp_start
-- 			from
-- 				lowest_level_dependency
-- 			join lowest_level_projects as predecessor on lowest_level_dependency.predecessor = predecessor.project
-- 			join lowest_level_projects as project on lowest_level_dependency.project = project.project
-- 			where
-- 				lowest_level_dependency.dependence = 'FS'
-- 			group by 
-- 				lowest_level_dependency.project
-- 			having
-- 				min(project.timestamp_start) < max(predecessor.timestamp_start + predecessor.worktime_planned)
-- 		);
		
-- 		update lowest_level_projects
-- 		set timestamp_start = updated_timestamp.predecessor_timestamp_finish
-- 		from updated_timestamp
-- 		where lowest_level_projects.project = updated_timestamp.project;
		
-- 		row_counter := (select count(*) from updated_timestamp);
		
-- 		drop table updated_timestamp;
-- 	end loop;
-- end $$;

-- select * from lowest_level_projects;
