from django.conf.urls import url
from django.urls import include
from rest_framework_swagger.views import get_swagger_view
# from djangoREST_tutorial.quickstart import views
from django.urls import include, path
from rest_framework import routers


schema_view = get_swagger_view(title='PMt API')


from ums.rawAPI.views import router as rawUMSRouter
from jobs.rawAPI.views import router as rawJobRouter
rawRouter = routers.DefaultRouter()
rawRouter.registry.extend(rawUMSRouter.registry)
rawRouter.registry.extend(rawJobRouter.registry)


from ums.userPerspectiveAPI.views import router as perspectiveUMSRouter
from jobs.userPerspectiveAPI.views import router as perspectiveJobRouter
upRouter = routers.DefaultRouter()
upRouter.registry.extend(perspectiveUMSRouter.registry)
upRouter.registry.extend(perspectiveJobRouter.registry)


urlpatterns = [
    url(r'^$', schema_view),
    # url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
    path('raw/', include(rawRouter.urls)),
    path('up/', include(upRouter.urls))
]
