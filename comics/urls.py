"""
Django router urls
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token

from comics.views import (ArcViewSet, IssueViewSet,
                          PublisherViewSet, SeriesViewSet)


ROUTER = routers.DefaultRouter()
ROUTER.register('arc', ArcViewSet)
ROUTER.register('issue', IssueViewSet)
ROUTER.register('publisher', PublisherViewSet)
ROUTER.register('series', SeriesViewSet)

app_name = 'api'
urlpatterns = [
    path('api/', include(ROUTER.urls)),
    path('api-token-auth/', obtain_jwt_token)
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
