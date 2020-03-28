import graphene
from graphene_django.types import DjangoObjectType, ObjectType
from graphene_django.filter import DjangoFilterConnectionField

import pmt_calendar.models as cal 





class Availability(DjangoObjectType):
    class Meta:
        model = cal.Availability
        filter_fields = '__all__'
    id = graphene.Int(required=True)





class Query(ObjectType):
    project = graphene.Field(Availability, id=graphene.Int())
    

    def resolve_project(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return cal.Availability.objects.get(pk=id)
        return None





class AvailabilityCreator(graphene.Mutation):
    class Arguments:
        start = graphene.String(required=True)
        end = graphene.String(required=True)
        repeat_interval = graphene.String()
        until = graphene.String()

    availability = graphene.Field(Availability)

    def mutate(self, info, start, end, repeat_interval=None, until=None):
        availability = cal.Availability.objects.create(creator_id=1, start=start, end=end, repeat_interval=repeat_interval, until=until)
        return AvailabilityCreator(availability=availability)


class Mutation(graphene.ObjectType):
    createAvailability = AvailabilityCreator.Field()
