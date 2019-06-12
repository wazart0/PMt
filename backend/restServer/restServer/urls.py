from django.conf.urls import url
from django.urls import include
from rest_framework_swagger.views import get_swagger_view
# from djangoREST_tutorial.quickstart import views
from django.urls import include, path
from rest_framework import routers

from ums.views import UserViewSet
from jobs.views import jobRouter


schema_view = get_swagger_view(title='PMt API')

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    url(r'^$', schema_view),
    # url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
    path('', include(router.urls)),
    path('jobs/', include(jobRouter.urls)),
]
