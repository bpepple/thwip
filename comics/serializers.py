from rest_framework import serializers

from comics.models import (Arc, Character, Creator,
                           Issue, Publisher, Series, Team)
from comics.utils.reader import ImageAPIHandler


class ComicPageSerializer(serializers.ModelSerializer):
    page = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Issue
        fields = ('page',)
        lookup_field = 'slug'

    def get_page(self, obj):
        page_number = self.context.get("page_number")
        i = ImageAPIHandler()
        data_uri = i.get_uri(obj.file, page_number)
        return data_uri


class IssueSerializer(serializers.HyperlinkedModelSerializer):
    series = serializers.SlugRelatedField(many=False, read_only=True,
                                          slug_field='slug')
    read_percentage = serializers.ReadOnlyField
    leaf = serializers.IntegerField()

    class Meta:
        model = Issue
        fields = ('__str__', 'slug', 'cvurl', 'series', 'name', 'number', 'date',
                  'leaf', 'page_count', 'read_percentage', 'status', 'desc', 'image')
        read_only_fields = ('__str__', 'slug', 'cvurl', 'name', 'number', 'date',
                            'page_count', 'read_percentage', 'desc', 'image')
        lookup_field = 'slug'


class PublisherSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Publisher
        fields = ('slug', 'cvurl', 'name', 'desc', 'image', 'series_count')
        lookup_field = 'slug'


class ReaderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Issue
        fields = ('leaf', 'page_count', 'status')


class SeriesImageSerializer(serializers.HyperlinkedModelSerializer):
    image = serializers.ImageField(
        max_length=None, use_url=True, allow_null=True, required=False)

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
