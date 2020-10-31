drop table if exists projects_in_tree;
drop table if exists project_edges;


create temp table projects_in_tree as (
	with recursive
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
	project_hierarchy as (
		select * from project_edges where edge_type_id = 'belongs_to'
	),
	project_tree as (
			select 
				s1.source_vertex_id, 
				s1.target_vertex_id, 
				cast(ROW_NUMBER() OVER () as varchar) AS wbs 
			from project_hierarchy as s1 
			where s1.target_vertex_id = {top_level_vertex_id}
		union all
			select 
				s2.source_vertex_id, 
				s2.target_vertex_id, 
				concat(s1.wbs, '.', cast(ROW_NUMBER() OVER () as varchar)) AS wbs 
			from project_hierarchy as s2, project_tree as s1 
			where s2.target_vertex_id = s1.source_vertex_id
	)
	select 
		source_vertex_id as project_id,
		target_vertex_id as belongs_to,
		wbs,
		project_project.worktime_planned,
		project_project.start,
		project_project.finish
	from project_tree
	left join project_project on project_tree.source_vertex_id = project_project.id
);

create temp table project_edges as (
	select
		*
	from
		ge_edge
	where 
		ge_edge.source_vertex_id in (select project_id from projects_in_tree)
	and
		ge_edge.target_vertex_id in (select project_id from projects_in_tree)
);

