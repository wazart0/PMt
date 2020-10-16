import graphene
from graphene_django.types import DjangoObjectType, ObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.core.exceptions import FieldError

import pmt_calendar.models as cal 
import ge.models as ge
import ums.models as ums




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
        user = graphene.Int(required=True)
        start = graphene.String(required=True)
        duration = graphene.String(required=True)
        repeat_interval = graphene.String()
        until = graphene.String()

    availability = graphene.Field(Availability)

    def mutate(self, info, user, start, duration, repeat_interval=None, until=None):
        user = ums.User.objects.get(pk=user)
        if user is None: # TODO check if it is enough
            raise FieldError('User not exits, ID: ' + str(user))
        availability = cal.Availability.objects.create(creator_id=1, start=start, duration=duration, repeat_interval=repeat_interval, until=until)
        if availability is None:
            raise FieldError('Cannot create availability - availability creation issue.')
        edge = ge.DirectedGraphModelManager.connect_nodes(ge.Vertex.objects.get(id=user.pk), ge.Vertex.objects.get(id=availability.pk), ge.EdgeType.objects.get(id='calendar'))
        if edge is None:
            raise FieldError('Cannot create availability - Edge creation issue.')
        return AvailabilityCreator(availability=availability)


# class AssignCalendarsToUser(graphene.Mutation):
#     class Arguments():
#         user = graphene.Int(required=True)
#         calendars = graphene.List(required=True)


class Mutation(graphene.ObjectType):
    createAvailability = AvailabilityCreator.Field()
