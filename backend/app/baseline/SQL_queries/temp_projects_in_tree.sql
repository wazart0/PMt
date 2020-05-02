drop table if exists projects_in_tree;
drop table if exists project_edges;


create temp table projects_in_tree as (
	with recursive
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
	project_hierarchy as (
		select * from project_edges where belongs_to = 'True'
	),
	project_tree as (
			select 
				s1.source_node, 
				s1.target_node, 
				cast(ROW_NUMBER() OVER () as varchar) AS wbs 
			from project_hierarchy as s1 
			where s1.target_node = 55
		union all
			select 
				s2.source_node, 
				s2.target_node, 
				concat(s1.wbs, '.', cast(ROW_NUMBER() OVER () as varchar)) AS wbs 
			from project_hierarchy as s2, project_tree as s1 
			where s2.target_node = s1.source_node
	)
	select 
		source_node as project,
		target_node as belongs_to,
		wbs
	from project_tree
);

create temp table project_edges as (
	select
		*
	from
		graph_engine_edge
	where 
		graph_engine_edge.source_node in (select project from projects_in_tree)
	and
		graph_engine_edge.target_node in (select project from projects_in_tree)
);

