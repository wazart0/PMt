with
project_edges as (
	select
		ge_edge.*
	from
		ge_edge 
	inner join
		project_project as source_project
	on 
		source_vertex_id = source_project.id
	inner join
		project_project as target_project
	on
		target_vertex_id = target_project.id
),
owns as (
	select 
		target_vertex_id as project_id, 
		source_vertex_id as own_id 
	from 
		project_edges 
	where 
		belongs_to = 'True'
),
lowest_level_dependency as (
	with
	unfiltered_dependency as (
		with recursive 
		dependence_edge as (
			select 
				project_edges.target_vertex_id as project_id,
				project_edges.source_vertex_id as predecessor_id,
				project_edges.timeline_dependency as dependence
			from 
				project_edges
			where
				timeline_dependency is not null
		),
		populate_project as (
				select 
					translation_project_id.project_id,
					own.own_id
				from dependence_edge as translation_project_id
				join owns as own
				on own.project_id = translation_project_id.project_id
			union 
				select 
					populate_project.project_id,
					own1.own_id
				from populate_project
				join owns as own1
				on own1.project_id = populate_project.own_id
		),
		populate_predecessors as (
				select 
					translation_predecessor_id.predecessor_id,
					own.own_id
				from dependence_edge as translation_predecessor_id
				join owns as own
				on own.project_id = translation_predecessor_id.predecessor_id
			union 
				select 
					populate_predecessors.predecessor_id,
					own1.own_id
				from populate_predecessors
				join owns as own1
				on own1.project_id = populate_predecessors.own_id
		)
		select 
			coalesce (populate_project.own_id, dependence_edge.project_id) as project_id,
			coalesce (populate_predecessors.own_id, dependence_edge.predecessor_id) as predecessor_id,
			dependence_edge.dependence as dependence
		from dependence_edge
		left join populate_project on dependence_edge.project_id = populate_project.project_id
		left join populate_predecessors on dependence_edge.predecessor_id = populate_predecessors.predecessor_id
	)
	select * 
	from unfiltered_dependency
	where 
		unfiltered_dependency.project_id not in (select project_id from owns)
	and
		unfiltered_dependency.predecessor_id not in (select project_id from owns)
),
lowest_level_projects as (
	select
		id as project_id,
		worktime_planned,
		cast ('2019-12-30 00:00:00-00' as timestamptz) as timestamp_start
	from
		project_project
	where
		id not in (select project_id from owns)
)





select
	lowest_level_dependency.project_id,
	max(predecessor.timestamp_start + predecessor.worktime_planned) as predecessor_timestamp_finish,
	min(project.timestamp_start) as project_timestamp_start
from
	lowest_level_dependency
join lowest_level_projects as predecessor on lowest_level_dependency.predecessor_id = predecessor.project_id
join lowest_level_projects as project on lowest_level_dependency.project_id = project.project_id
where
	lowest_level_dependency.dependence = 'FS'
group by 
	lowest_level_dependency.project_id
having
	min(project.timestamp_start) < max(predecessor.timestamp_start + predecessor.worktime_planned)

	
;