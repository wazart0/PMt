drop table project_edges;
drop table owns;
drop table lowest_level_dependency;
drop table lowest_level_projects;

create temp table project_edges as (
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
);

create temp table owns as (
	select 
		target_node as project, 
		source_node as own 
	from 
		project_edges 
	where 
		belongs_to = 'True'
);

create temp table lowest_level_dependency as (
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
);

create temp table lowest_level_projects as (
	select
		id as project,
		worktime_planned,
		cast ('2019-12-30 00:00:00-00' as timestamptz) as timestamp_start
	from
		project_project
	where
		id not in (select project from owns)
);





select
	lowest_level_dependency.project,
	max(predecessor.timestamp_start + predecessor.worktime_planned) as predecessor_timestamp_end,
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


;