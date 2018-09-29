from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token

from comics.views import (ArcViewSet, IssueViewSet,
                          PublisherViewSet, SeriesViewSet)


router = routers.DefaultRouter()
router.register('arc', ArcViewSet)
router.register('issue', IssueViewSet)
router.register('publisher', PublisherViewSet)
router.register('series', SeriesViewSet)

app_name = 'api'
urlpatterns = [
    path('api/', include(router.urls)),
    path('api-token-auth/', obtain_jwt_token)
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
