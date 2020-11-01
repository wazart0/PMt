drop table if exists temp_filtered_user_calendar;
drop table if exists temp_filtered_calendar;


create temp table temp_filtered_user_calendar as (
	select * from user_calendar 
	where 
		user_id in (select id from public.user)
	and
		(finish > '{start_date}' or finish is null)
);


create temp table temp_filtered_calendar as (
	select * from calendar where id in (select calendar_id from temp_filtered_user_calendar)
);
