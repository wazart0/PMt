
alter table lowest_level_projects 
	add column timestamp_begin timestamptz default cast('2019-12-30 00:00:00-00' as timestamptz);


do $$
declare 
	row_counter integer := 1;
begin
	while row_counter > 0 loop
		create temp table updated_timestamp as (
			select
				lowest_level_dependancy.project_id as project_id,
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
		);
		
		update lowest_level_projects
		set timestamp_begin = updated_timestamp.predecessor_timestamp_end
		from updated_timestamp
		where lowest_level_projects.project_id = updated_timestamp.project_id;
		
		row_counter := (select count(*) from updated_timestamp);
		
		drop table updated_timestamp;
	end loop;
end $$;

select * from lowest_level_projects;
