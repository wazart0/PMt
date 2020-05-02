
alter table lowest_level_projects 
	add column timestamp_start timestamptz default cast('2019-12-30 00:00:00-00' as timestamptz);


do $$
declare 
	row_counter integer := 1;
start
	while row_counter > 0 loop
		create temp table updated_timestamp as (
			select
				lowest_level_dependency.project_id as project_id,
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
		);
		
		update lowest_level_projects
		set timestamp_start = updated_timestamp.predecessor_timestamp_finish
		from updated_timestamp
		where lowest_level_projects.project_id = updated_timestamp.project_id;
		
		row_counter := (select count(*) from updated_timestamp);
		
		drop table updated_timestamp;
	end loop;
end $$;

select * from lowest_level_projects;
