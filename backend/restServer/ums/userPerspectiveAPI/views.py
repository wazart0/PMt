from django.shortcuts import render
from rest_framework import viewsets, mixins, routers, status
from rest_framework.response import Response
from rest_framework.settings import api_settings

from ums.userPerspectiveAPI.serializers import *


def userAuthorizedUMS(userID):
    return User.objects.all().filter()


class UserViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = User.objects.all().filter(pk = 0)
    serializer_class = UserSerializer
    lookup_field = 'user_id'

    def list(self, request, user_id):
        queryset = self.filter_queryset(userAuthorizedUMS(user_id))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # def perform_create(self, serializer):
    #     serializer.save()

    # def get_success_headers(self, data):
    #     try:
    #         return {'Location': str(data[api_settings.URL_FIELD_NAME])}
    #     except (TypeError, KeyError):
    #         return {}



router = routers.SimpleRouter()
router.register(r'(?P<user_id>.+)/user', UserViewSet)
