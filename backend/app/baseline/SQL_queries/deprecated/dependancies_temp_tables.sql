drop table project_edges;
drop table owns;
drop table lowest_level_dependancy;
drop table lowest_level_projects;

create temp table project_edges as (
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
);

create temp table owns as (
	select 
		target_node_id as project_id, 
		source_node_id as own_id 
	from 
		project_edges 
	where 
		belongs_to = 'True'
);

create temp table lowest_level_dependancy as (
	with
	unfiltered_dependancy as (
		with recursive 
		dependance_edge as (
			select 
				project_edges.target_node_id as project_id,
				project_edges.source_node_id as predecessor_id,
				project_edges.timeline_dependancy as dependance
			from 
				project_edges
			where
				timeline_dependancy is not null
		),
		populate_project as (
				select 
					translation_project_id.project_id,
					own.own_id
				from dependance_edge as translation_project_id
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
				from dependance_edge as translation_predecessor_id
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
			coalesce (populate_project.own_id, dependance_edge.project_id) as project_id,
			coalesce (populate_predecessors.own_id, dependance_edge.predecessor_id) as predecessor_id,
			dependance_edge.dependance as dependance
		from dependance_edge
		left join populate_project on dependance_edge.project_id = populate_project.project_id
		left join populate_predecessors on dependance_edge.predecessor_id = populate_predecessors.predecessor_id
	)
	select * 
	from unfiltered_dependancy
	where 
		unfiltered_dependancy.project_id not in (select project_id from owns)
	and
		unfiltered_dependancy.predecessor_id not in (select project_id from owns)
);

create temp table lowest_level_projects as (
	select
		id as project_id,
		worktime_planned,
		cast ('2019-12-30 00:00:00-00' as timestamptz) as timestamp_begin
	from
		project_project
	where
		id not in (select project_id from owns)
);





select
	lowest_level_dependancy.project_id,
	max(predecessor.timestamp_begin + predecessor.worktime_planned) as predecessor_timestamp_end,
	min(project.timestamp_begin) as project_timestamp_begin
from
	lowest_level_dependancy
join lowest_level_projects as predecessor on lowest_level_dependancy.predecessor_id = predecessor.project_id
join lowest_level_projects as project on lowest_level_dependancy.project_id = project.project_id
where
	lowest_level_dependancy.dependance = 'FS'
group by 
	lowest_level_dependancy.project_id
having
	min(project.timestamp_begin) < max(predecessor.timestamp_begin + predecessor.worktime_planned)


;