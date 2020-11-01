drop table if exists projects_in_tree;
drop table if exists projects_dependency;


create temp table projects_in_tree as (
	with recursive 
	projects_to_search as (
		select 
			project_id,
			parent_id,
			start,
			finish,
			worktime
		from baseline_project where 
			baseline_id = '{source_baseline_id}'
	),
	project_tree as (

		select s1.* from projects_to_search as s1 
		where s1.project_id = '{project_id}'

		union all

		select s2.* from projects_to_search as s2, project_tree as s1 
		where s2.parent_id = s1.project_id

	)
	select * from project_tree
);


create temp table projects_dependency as (
	select 
		project_id,
		predecessor_id,
		type
	from baseline_project_dependency 
	where
		baseline_id = '{source_baseline_id}'
	and
		project_id in (select project_id from projects_in_tree)
	and
		predecessor_id in (select project_id from projects_in_tree)
);
