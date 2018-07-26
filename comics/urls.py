from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework import routers

from comics.views import (IssueViewSet, PublisherViewSet, SeriesViewSet)


router = routers.DefaultRouter()
router.register('issue', IssueViewSet)
router.register('publisher', PublisherViewSet)
router.register('series', SeriesViewSet)

app_name = 'api'
urlpatterns = [
    path('api/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
