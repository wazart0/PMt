import graphene
from graphene_django.types import DjangoObjectType, ObjectType
import jobs.models as jobs



class Job(DjangoObjectType):
    class Meta:
        model = jobs.Job


class Milestone(DjangoObjectType):
    class Meta:
        model = jobs.Milestone


class JobAuthorization(DjangoObjectType):
    class Meta:
        model = jobs.JobAuthorization


class Privileges(DjangoObjectType):
    class Meta:
        model = jobs.Privileges


class Status(DjangoObjectType):
    class Meta:
        model = jobs.Status


class Type(DjangoObjectType):
    class Meta:
        model = jobs.Type


class TypeStatuses(DjangoObjectType):
    class Meta:
        model = jobs.TypeStatuses


class Baseline(DjangoObjectType):
    class Meta:
        model = jobs.Baseline


class Execution(DjangoObjectType):
    class Meta:
        model = jobs.Execution


class ReportedWorkTime(DjangoObjectType):
    class Meta:
        model = jobs.ReportedWorkTime



class Query(ObjectType):
    job = graphene.Field(Job, id=graphene.Int())
    milestone = graphene.Field(Milestone, id=graphene.Int())
    jobs = graphene.List(Job)
    milestones = graphene.List(Milestone)

    def resolve_actor(self, info, **kwargs):
        id = kwargs.get('id')

        if id is not None:
            return Actor.objects.get(pk=id)

        return None

    def resolve_movie(self, info, **kwargs):
        id = kwargs.get('id')

        if id is not None:
            return Movie.objects.get(pk=id)

        return None

    def resolve_actors(self, info, **kwargs):
        return Actor.objects.all()

    def resolve_movies(self, info, **kwargs):
        return Movie.objects.all()



# schema = graphene.Schema(query=Query, mutation=None)
