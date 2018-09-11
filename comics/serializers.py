from rest_framework import serializers

from comics.models import (Credits, Issue, Publisher, Role, Series)
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


class RoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        fields = ('id', 'name')


class CreditsSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source='creator.name')
    image = serializers.ImageField(source='creator.image')
    role = RoleSerializer('role', many=True)

    class Meta:
        model = Credits
        fields = ('id', 'creator', 'image', 'role')


class IssueSerializer(serializers.ModelSerializer):
    series = serializers.SlugRelatedField(many=False, read_only=True,
                                          slug_field='slug')
    credits = CreditsSerializer(source='credits_set', many=True,
                                read_only=True)
    percent_read = serializers.ReadOnlyField
    leaf = serializers.IntegerField()

    class Meta:
        model = Issue
        fields = ('id', '__str__', 'slug', 'cvurl', 'series', 'name', 'number', 'date',
                  'leaf', 'page_count', 'percent_read', 'status', 'desc', 'image',
                  'credits')
        read_only_fields = ('id', '__str__', 'slug', 'cvurl', 'name', 'number', 'date',
                            'page_count', 'desc', 'image')
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
    percent_read = serializers.ReadOnlyField
    image = SeriesImageSerializer(source='issue_set.first', many=False)

    class Meta:
        model = Series
        fields = ('slug', 'cvurl', 'name', 'sort_title', 'publisher',
                  'year', 'desc', 'issue_count', 'percent_read',
                  'image')
        lookup_field = 'slug'

    def to_representation(self, obj):
        """ Move image field from Issue to Series representation. """
        representation = super().to_representation(obj)
        issue_representation = representation.pop('image')
        for key in issue_representation:
            representation[key] = issue_representation[key]

        return representation
