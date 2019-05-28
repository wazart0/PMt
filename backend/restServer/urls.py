"""

Author: Artur Waz

Date: 28/05/2019

"""

## tutorial of default django url

# from django.contrib import admin
# from django.urls import path

# urlpatterns = [
#     path('admin/', admin.site.urls),
# ]


## swagger rest framework

from django.conf.urls import url
from django.urls import include
from rest_framework_swagger.views import get_swagger_view
from app import views
from django.urls import include, path
from rest_framework import routers

schema_view = get_swagger_view(title='PMt API')


router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

urlpatterns = [
    url(r'^$', schema_view),
    # url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
    path('', include(router.urls)),
]
