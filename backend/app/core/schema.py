import graphene
import ums.schema
import project.schema
import pmt_calendar.schema
import baseline.schema
# import jobs.userPerspectiveAPI.schema
# import ge.schema

class Query(
    # ge.schema.Query,
    ums.schema.Query, 
    project.schema.Query,
    pmt_calendar.schema.Query,
    baseline.schema.Query,
    # jobs.userPerspectiveAPI.schema.Query,
    graphene.ObjectType
    ):
    # This class will inherit from multiple Queries
    # as we begin to add more apps to our project
    pass

class Mutation(
    ums.schema.Mutation, 
    project.schema.Mutation,
    pmt_calendar.schema.Mutation,
    baseline.schema.Mutation,
    graphene.ObjectType):
    # This class will inherit from multiple Queries
    # as we begin to add more apps to our project
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)