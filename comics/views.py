from rest_framework import viewsets, permissions
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from comics.models import (Arc, Character, Creator,
                           Issue, Publisher, Series,
                           Team)
from comics.serializers import (ArcSerializer, CharacterSerializer,
                                CreatorSerializer, IssueSerializer,
                                PublisherSerializer, SeriesSerializer,
                                TeamSerializer)


class ArcViewSet(viewsets.ReadOnlyModelViewSet):
    """
    get:
    Returns a list of all the story arcs.

    retrieve:
    Returns the information of an individual story arc.
    """
    queryset = Arc.objects.all()
    serializer_class = ArcSerializer
    lookup_field = 'slug'
    permission_classes = (permissions.IsAuthenticated,)


class CharacterViewSet(viewsets.ReadOnlyModelViewSet):
    """
    get:
    Returns a list of all the characters.

    retrieve:
    Returns the information for an individual character.
    """
    queryset = (
        Character.objects
        .prefetch_related('teams')
    )
    serializer_class = CharacterSerializer
    lookup_field = 'slug'
    permission_classes = (permissions.IsAuthenticated,)


class CreatorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    get:
    Returns a list of all creators.

    retrieve:
    Returns the information of an individual creator.
    """
    queryset = Creator.objects.all()
    serializer_class = CreatorSerializer
    lookup_field = 'slug'
    permission_classes = (permissions.IsAuthenticated,)


class IssueViewSet(viewsets.ReadOnlyModelViewSet):
    """
    get:
    Returns a list of all issues.

    retrieve:
    Returns the information of an individual issue.
    """
    queryset = (
        Issue.objects
        .select_related('series')
        .prefetch_related('arcs', 'characters', 'teams')
    )
    serializer_class = IssueSerializer
    lookup_field = 'slug'
    permission_classes = (permissions.IsAuthenticated,)


class PublisherViewSet(viewsets.ReadOnlyModelViewSet):
    """
    get:
    Returns a list of all publishers.

    retrieve:
    Returns the information of an individual publisher.
    """
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    lookup_field = 'slug'
    permission_classes = (permissions.IsAuthenticated,)

    @detail_route()
    def series_list(self, request, slug=None):
        """
        Returns a list of series for a publisher.
        """
        publisher = self.get_object()
        series = Series.objects.filter(publisher__slug=publisher.slug)
        series_json = SeriesSerializer(series, many=True)
        return Response(series_json.data)


class SeriesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    get:
    Returns a list of all the comic series.

    retrieve:
    Returns the information of an individual comic series.
    """
    queryset = (
        Series.objects
        .select_related('publisher')
    )
    serializer_class = SeriesSerializer
    lookup_field = 'slug'
    permission_classes = (permissions.IsAuthenticated,)

    @detail_route()
    def issue_list(self, request, slug=None):
        """
        Returns a list of issues for a series.
        """
        series = self.get_object()
        issues = Issue.objects.filter(series__slug=series.slug)
        issues_json = IssueSerializer(issues, many=True)
        return Response(issues_json.data)


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    """
    get:
    Returns a list of all the teams.

    retrieve:
    Returns the information for an individual team.
    """
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    lookup_field = 'slug'
    permission_classes = (permissions.IsAuthenticated,)
