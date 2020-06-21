create temp table lowest_level_dependency as (
	with
	owns as (
		select 
			target_vertex_id as project_id, 
			source_vertex_id as own_id 
		from 
			project_edges 
		where 
			edge_type_id = 'belongs_to'
	),
	lowest_level_dependence as (
		with
		unfiltered_dependency as (
			with recursive 
			dependence_edge as (
				select 
					project_edges.target_vertex_id as project_id,
					project_edges.source_vertex_id as predecessor_id,
					project_edges.details->>'type' as dependence
				from 
					project_edges
				where
					edge_type_id = 'dependence'
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
	)
	select * from lowest_level_dependence
	where 
		project_id in (select project_id from projects_in_tree)
	and
		predecessor_id in (select project_id from projects_in_tree)
);
