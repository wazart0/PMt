import graphene
import ums.schema
import project.schema
# import jobs.userPerspectiveAPI.schema
# import graph_engine.schema

class Query(
    # graph_engine.schema.Query,
    ums.schema.Query, 
    project.schema.Query,
    # jobs.userPerspectiveAPI.schema.Query,
    graphene.ObjectType
    ):
    # This class will inherit from multiple Queries
    # as we begin to add more apps to our project
    pass

class Mutation(
    ums.schema.Mutation, 
    project.schema.Mutation,
    graphene.ObjectType):
    # This class will inherit from multiple Queries
    # as we begin to add more apps to our project
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)