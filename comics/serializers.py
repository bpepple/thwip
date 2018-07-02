from rest_framework import serializers

from comics.models import (Arc, Character, Creator,
                           Issue, Publisher, Series, Team)


class IssueSerializer(serializers.HyperlinkedModelSerializer):
    series = serializers.SlugRelatedField(many=False, read_only=True,
                                          slug_field='slug')
    read_percentage = serializers.ReadOnlyField

    class Meta:
        model = Issue
        fields = ('__str__', 'slug', 'cvurl', 'series', 'name', 'number', 'date',
                  'leaf', 'page_count', 'read_percentage', 'status', 'desc', 'image')
        lookup_field = 'slug'


class PublisherSerializer(serializers.HyperlinkedModelSerializer):
    serie_count = serializers.ReadOnlyField

    class Meta:
        model = Publisher
        fields = ('slug', 'cvurl', 'name', 'desc', 'image', 'series_count')
        lookup_field = 'slug'


class SeriesImageSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Issue
        fields = ('image',)
        lookup_field = 'slug'


class SeriesSerializer(serializers.HyperlinkedModelSerializer):
    publisher = serializers.SlugRelatedField(many=False, read_only=True,
                                             slug_field='slug')
    issue_count = serializers.ReadOnlyField
    image = SeriesImageSerializer(source='issue_set.first', many=False)

    class Meta:
        model = Series
        fields = ('slug', 'cvurl', 'name', 'sort_title', 'publisher',
                  'year', 'desc', 'issue_count', 'image')
        lookup_field = 'slug'

    def to_representation(self, obj):
        """ Move image field from Issue to Series representation. """
        representation = super().to_representation(obj)
        issue_representation = representation.pop('image')
        for key in issue_representation:
            representation[key] = issue_representation[key]

        return representation


class CreatorSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Creator
        fields = ('slug', 'cvurl', 'name', 'desc', 'image')
        lookup_field = 'slug'


class CharacterSerializer(serializers.HyperlinkedModelSerializer):
    teams = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name='api:team-detail', lookup_field='slug')

    class Meta:
        model = Character
        fields = ('slug', 'cvurl', 'name', 'teams', 'desc', 'image')
        lookup_field = 'slug'


class TeamSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Team
        fields = ('slug', 'cvurl', 'name', 'desc', 'image')
        lookup_field = 'slug'


class ArcSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Arc
        fields = ('slug', 'cvurl', 'name', 'desc', 'image')
        lookup_field = 'slug'
