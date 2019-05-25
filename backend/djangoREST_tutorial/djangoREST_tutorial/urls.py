"""djangoREST_tutorial URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
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
from djangoREST_tutorial.quickstart import views
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