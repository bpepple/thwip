import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.request import Request
from rest_framework.test import APIClient, APITestCase
from rest_framework.test import APIRequestFactory

from comics.models import Series, Publisher
from comics.serializers import SeriesSerializer


class GetAllSeriesTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        publisher_obj = Publisher.objects.create(
            name='DC Comics', slug='dc-comics')
        Series.objects.create(cvid='1234', cvurl='http://1.com',
                              name='Superman', slug='superman', publisher=publisher_obj)
        Series.objects.create(cvid='4321', cvurl='http://2.com',
                              name='Batman', slug='batman', publisher=publisher_obj)

    def setUp(self):
        self.email = 'brian@test.com'
        self.username = 'brian'
        self.password = 'test!thwip'
        self.user = User.objects.create_user(
            self.username, self.email, self.password)

        self.client = APIClient()
        self.token = Token.objects.get(user__username=self.username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('api:series-list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(len(json.loads(resp.content))
                        == Series.objects.count())

    def test_unauthorized_view_url(self):
        # Clear the credentials.
        self.client.credentials()
        resp = self.client.get(reverse('api:series-list'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class GetSingleSeriesTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        factory = APIRequestFactory()
        request = factory.get('/')

        cls.serializer_context = {
            'request': Request(request),
        }

        publisher_obj = Publisher.objects.create(name='Marvel', slug='marvel')
        cls.thor = Series.objects.create(cvid='1234', cvurl='https://comicvine.com',
                                         name='The Mighty Thor', slug='the-mighty-thor',
                                         publisher=publisher_obj)

    def setUp(self):
        self.email = 'tom@test.com'
        self.username = 'tom'
        self.password = 'test!thwip'
        self.user = User.objects.create_user(
            self.username, self.email, self.password)

        self.client = APIClient()
        self.token = Token.objects.get(user__username=self.username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_get_valid_single_series(self):
        resp = self.client.get(
            reverse('api:series-detail', kwargs={'slug': self.thor.slug}))
        series = Series.objects.get(slug=self.thor.slug)
        serializer = SeriesSerializer(series, context=self.serializer_context)
        self.assertEqual(resp.data, serializer.data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_invalid_single_series(self):
        response = self.client.get(
            reverse('api:arc-detail', kwargs={'slug': 'batman'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthorized_view_url(self):
        # Clear the credentials.
        self.client.credentials()
        response = self.client.get(
            reverse('api:series-detail', kwargs={'slug': self.thor.slug}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
