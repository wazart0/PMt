drop table if exists availability;

create temp table availability as (
	with
	users as (
		select id from ums_user
	),
	selected_availability as (
		select 
			pmt_calendar_availability.id as id,
			ge_edge.source_vertex_id as user_id,
			pmt_calendar_availability.start,
			pmt_calendar_availability.duration,
			pmt_calendar_availability.repeat_interval,
			pmt_calendar_availability.until	
		from ge_edge
		inner join pmt_calendar_availability on ge_edge.target_vertex_id = pmt_calendar_availability.id
		where 
			ge_edge.source_vertex_id in (select * from users)
		and
			ge_edge.edge_type_id = 'calendar'
	),
	availability as (
		select 
			id,
			user_id,
			generate_series(selected_availability.start, coalesce (selected_availability.until, timestamptz '2022-12-30'), selected_availability.repeat_interval) as start,
			generate_series(selected_availability.start + selected_availability.duration, coalesce (selected_availability.until, timestamptz '2022-12-30'), selected_availability.repeat_interval) as finish
		from
			selected_availability
	)
	select * from availability 
	where start > timestamptz '{start}'
	order by start asc
);

