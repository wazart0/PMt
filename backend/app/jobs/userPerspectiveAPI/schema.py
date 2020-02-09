# import graphene
# from graphene_django.types import DjangoObjectType, ObjectType
# import jobs.models as jobsM



# class Job(DjangoObjectType):
#     class Meta:
#         model = jobsM.Job


# class Milestone(DjangoObjectType):
#     class Meta:
#         model = jobsM.Milestone


# class JobAuthorization(DjangoObjectType):
#     class Meta:
#         model = jobsM.JobAuthorization


# class Privileges(DjangoObjectType):
#     class Meta:
#         model = jobsM.Privileges


# class Status(DjangoObjectType):
#     class Meta:
#         model = jobsM.Status


# class Type(DjangoObjectType):
#     class Meta:
#         model = jobsM.Type


# class TypeStatuses(DjangoObjectType):
#     class Meta:
#         model = jobsM.TypeStatuses


# class Baseline(DjangoObjectType):
#     class Meta:
#         model = jobsM.Baseline


# class Execution(DjangoObjectType):
#     class Meta:
#         model = jobsM.Execution


# class ReportedWorkTime(DjangoObjectType):
#     class Meta:
#         model = jobsM.ReportedWorkTime



# class Query(ObjectType):
#     job = graphene.Field(Job, id=graphene.Int())
#     milestone = graphene.Field(Milestone, id=graphene.Int())
#     jobs = graphene.List(Job)
#     milestones = graphene.List(Milestone)

#     def resolve_job(self, info, **kwargs):
#         id = kwargs.get('id')

#         if id is not None:
#             return jobsM.Job.objects.get(pk=id)

#         return None

#     def resolve_milestone(self, info, **kwargs):
#         id = kwargs.get('id')

#         if id is not None:
#             return jobsM.Milestone.objects.get(pk=id)

#         return None

#     def resolve_jobs(self, info, **kwargs):
#         return jobsM.Job.objects.all()

#     def resolve_milestones(self, info, **kwargs):
#         return jobsM.Milestone.objects.all()



# # schema = graphene.Schema(query=Query, mutation=None)
