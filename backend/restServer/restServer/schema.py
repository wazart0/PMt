import graphene
import ums.userPerspectiveAPI.schema

class Query(ums.userPerspectiveAPI.schema.Query, graphene.ObjectType):
    # This class will inherit from multiple Queries
    # as we begin to add more apps to our project
    pass

# class Mutation(ums.userPerspectiveAPI.schema.Mutation, graphene.ObjectType):
#     # This class will inherit from multiple Queries
#     # as we begin to add more apps to our project
#     pass

schema = graphene.Schema(query=Query, mutation=None)