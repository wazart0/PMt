create temp table availability as (
	with
	users as (
		select id from ums_user
	),
	selected_availability as (
		select 
			pmt_calendar_availability.id as id,
			graph_engine_edge.source_node_id as user_id,
			pmt_calendar_availability.start,
			pmt_calendar_availability.duration,
			pmt_calendar_availability.repeat_interval,
			pmt_calendar_availability.until	
		from graph_engine_edge
		inner join pmt_calendar_availability on graph_engine_edge.target_node_id = pmt_calendar_availability.id
		where 
			graph_engine_edge.source_node_id in (select * from users)
		and
			graph_engine_edge.assignee = 'True'
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
	where start > timestamptz '2020-02-01'
	order by start asc
);