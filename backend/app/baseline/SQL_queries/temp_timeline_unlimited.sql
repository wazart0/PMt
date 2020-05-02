
alter table lowest_level_projects 
	add column timestamp_start timestamptz default cast('2019-12-30 00:00:00-00' as timestamptz);


do $$
declare 
	row_counter integer := 1;
start
	while row_counter > 0 loop
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
		
		update lowest_level_projects
		set timestamp_start = updated_timestamp.predecessor_timestamp_finish
		from updated_timestamp
		where lowest_level_projects.project = updated_timestamp.project;
		
		row_counter := (select count(*) from updated_timestamp);
		
		drop table updated_timestamp;
	end loop;
end $$;

select * from lowest_level_projects;
