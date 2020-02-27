import graphene
from graphene_django.types import DjangoObjectType, ObjectType
from graphene_django.filter import DjangoFilterConnectionField

# from django.db.models.expressions import RawSQL
from django.db import connection

import baseline.models as bl
import graph_engine.models as ge
import project.models as pj




# lowest_level_projects_worktime = '''
# select 
# 	id, 
# 	worktime_planned
# from 
# 	project_project
# where 
# 	id not in
# 		(select 
# 			edge.target_node_id
# 		from 
# 			project_project
# 		join 
# 			(select 
# 			 	source_node_id, 
# 			 	target_node_id 
# 			 from 
# 			 	graph_engine_edge 
# 			 where belongs_to = 'True') as edge 
# 		 on edge.source_node_id = project_project.id);
# '''

# TODO check to be added if the output is unique and protection against looped queries
lowest_level_projects_dependancy = '''
with
project_edges as (
	select
		graph_engine_edge.*
	from
		graph_engine_edge 
	inner join
		project_project as source_project
	on 
		source_node_id = source_project.id
	inner join
		project_project as target_project
	on
		target_node_id = target_project.id
),
owns as (
	select 
		target_node_id as project_id, 
		source_node_id as own_id 
	from 
		project_edges 
	where 
		belongs_to = 'True'
),
lowest_level_dependancy as (
	with
	unfiltered_dependancy as (
		with recursive 
		dependance_edge as (
			select 
				project_edges.target_node_id as project_id,
				project_edges.source_node_id as predecessor_id,
				project_edges.timeline_dependancy as dependance
			from 
				project_edges
			where
				timeline_dependancy is not null
		),
		populate_project as (
				select 
					translation_project_id.project_id,
					own.own_id
				from dependance_edge as translation_project_id
				join owns as own
				on own.project_id = translation_project_id.project_id
			union 
				select 
					populate_project.project_id,
					own1.own_id
				from populate_project
				join owns as own1
				on own1.project_id = populate_project.own_id
		),
		populate_predecessors as (
				select 
					translation_predecessor_id.predecessor_id,
					own.own_id
				from dependance_edge as translation_predecessor_id
				join owns as own
				on own.project_id = translation_predecessor_id.predecessor_id
			union 
				select 
					populate_predecessors.predecessor_id,
					own1.own_id
				from populate_predecessors
				join owns as own1
				on own1.project_id = populate_predecessors.own_id
		)
		select 
			coalesce (populate_project.own_id, dependance_edge.project_id) as project_id,
			coalesce (populate_predecessors.own_id, dependance_edge.predecessor_id) as predecessor_id,
			dependance_edge.dependance as dependance
		from dependance_edge
		left join populate_project on dependance_edge.project_id = populate_project.project_id
		left join populate_predecessors on dependance_edge.predecessor_id = populate_predecessors.predecessor_id
	)
	select * 
	from unfiltered_dependancy
	where 
		unfiltered_dependancy.project_id not in (select project_id from owns)
	and
		unfiltered_dependancy.predecessor_id not in (select project_id from owns)
)
select 
	lowest_level_dependancy.*,
	project.name as project_name,
	predecessor.name as predecessor_name
from
	lowest_level_dependancy

left join project_project as project on project_id = project.id
left join project_project as predecessor on predecessor_id = predecessor.id
order by
	project_id,
	predecessor_id
'''


tmp_time_calculator = '''
with
project_edges as (
	select
		graph_engine_edge.*
	from
		graph_engine_edge 
	inner join
		project_project as source_project
	on 
		source_node_id = source_project.id
	inner join
		project_project as target_project
	on
		target_node_id = target_project.id
),
owns as (
	select 
		target_node_id as project_id, 
		source_node_id as own_id 
	from 
		project_edges 
	where 
		belongs_to = 'True'
),
lowest_level_dependancy as (
	with
	unfiltered_dependancy as (
		with recursive 
		dependance_edge as (
			select 
				project_edges.target_node_id as project_id,
				project_edges.source_node_id as predecessor_id,
				project_edges.timeline_dependancy as dependance
			from 
				project_edges
			where
				timeline_dependancy is not null
		),
		populate_project as (
				select 
					translation_project_id.project_id,
					own.own_id
				from dependance_edge as translation_project_id
				join owns as own
				on own.project_id = translation_project_id.project_id
			union 
				select 
					populate_project.project_id,
					own1.own_id
				from populate_project
				join owns as own1
				on own1.project_id = populate_project.own_id
		),
		populate_predecessors as (
				select 
					translation_predecessor_id.predecessor_id,
					own.own_id
				from dependance_edge as translation_predecessor_id
				join owns as own
				on own.project_id = translation_predecessor_id.predecessor_id
			union 
				select 
					populate_predecessors.predecessor_id,
					own1.own_id
				from populate_predecessors
				join owns as own1
				on own1.project_id = populate_predecessors.own_id
		)
		select 
			coalesce (populate_project.own_id, dependance_edge.project_id) as project_id,
			coalesce (populate_predecessors.own_id, dependance_edge.predecessor_id) as predecessor_id,
			dependance_edge.dependance as dependance
		from dependance_edge
		left join populate_project on dependance_edge.project_id = populate_project.project_id
		left join populate_predecessors on dependance_edge.predecessor_id = populate_predecessors.predecessor_id
	)
	select * 
	from unfiltered_dependancy
	where 
		unfiltered_dependancy.project_id not in (select project_id from owns)
	and
		unfiltered_dependancy.predecessor_id not in (select project_id from owns)
),
lowest_level_projects as (
	select
		id as project_id,
		name as project_name,
		worktime_planned,
		cast ('2019-12-30 00:00:00-00' as timestamptz) as timestamp_begin
	from
		project_project
	where
		id not in (select project_id from owns)
)

select
	lowest_level_dependancy.project_id,
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
'''


def retrieve_data_from_db():
    return pj.Project.objects.all()


# def 



class TimeLine(ObjectType):
    pass




class Query(ObjectType):
    pass
    # project = graphene.Field(Project, id=graphene.Int())
    # projects = graphene.List(Project)
    
    # projectFilter = DjangoFilterConnectionField(ProjectFilter)

    # def resolve_project(self, info, **kwargs):
    #     id = kwargs.get('id')
    #     if id is not None:
    #         return pjt.Project.objects.get(pk=id)
    #     return None

    # def resolve_projects(self, info, **kwargs):
    #     return pjt.Project.objects.all()


