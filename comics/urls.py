from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken import views as drf_views

from comics.views import (ArcViewSet, CharacterViewSet,
                          CreatorViewSet, IssueViewSet,
                          PublisherViewSet, SeriesViewSet,
                          TeamViewSet)


router = routers.DefaultRouter()
router.register('arc', ArcViewSet)
router.register('character', CharacterViewSet)
router.register('creator', CreatorViewSet)
router.register('issue', IssueViewSet)
router.register('publisher', PublisherViewSet)
router.register('series', SeriesViewSet)
router.register('team', TeamViewSet)

app_name = 'api'
urlpatterns = [
    path('api/', include(router.urls)),
    path('api-token-auth/', drf_views.obtain_auth_token),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
