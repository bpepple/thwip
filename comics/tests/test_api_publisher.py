import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from comics.models import Publisher
from comics.serializers import PublisherSerializer


class GetAllPublisherTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        Publisher.objects.create(name='DC Comics', slug='dc-comics')
        Publisher.objects.create(name='Marvel', slug='marvel')

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
        resp = self.client.get(reverse('api:publisher-list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(len(json.loads(resp.content))
                        == Publisher.objects.count())

    def test_unauthorized_view_url(self):
        # Clear the credentials.
        self.client.credentials()
        resp = self.client.get(reverse('api:publisher-list'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class GetSinglePublisherTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.dc = Publisher.objects.create(name='DC Comics', slug='dc-comics')
        cls.marvel = Publisher.objects.create(name='Marvel', slug='marvel')

    def setUp(self):
        self.email = 'tom@test.com'
        self.username = 'tom'
        self.password = 'test!thwip'
        self.user = User.objects.create_user(
            self.username, self.email, self.password)

        self.client = APIClient()
        self.token = Token.objects.get(user__username=self.username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_get_valid_single_publisher(self):
        response = self.client.get(
            reverse('api:publisher-detail', kwargs={'slug': self.dc.slug}))
        publisher = Publisher.objects.get(slug=self.dc.slug)
        serializer = PublisherSerializer(publisher)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_invalid_single_publisher(self):
        response = self.client.get(
            reverse('api:publisher-detail', kwargs={'slug': 'dark-horse'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthorized_view_url(self):
        # Clear the credentials.
        self.client.credentials()
        response = self.client.get(
            reverse('api:publisher-detail', kwargs={'slug': self.dc.slug}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
