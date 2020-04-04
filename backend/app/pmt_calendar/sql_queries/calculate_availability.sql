with
availability as (
	select 
		id,
		generate_series(pmt_calendar_availability.start, timestamptz '2020-12-30', pmt_calendar_availability.repeat_interval) as start,
		generate_series(pmt_calendar_availability.end, timestamptz '2020-12-30', pmt_calendar_availability.repeat_interval) as end
	from
		pmt_calendar_availability
)
select * from availability 
where start > timestamptz '2020-02-01'
order by start asc
;