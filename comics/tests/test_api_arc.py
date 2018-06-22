import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from comics.models import Arc
from comics.serializers import ArcSerializer


class GetAllArcsTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        Arc.objects.create(cvid='1234', cvurl='http://1.com',
                           name='World War Hulk', slug='world-war-hulk')
        Arc.objects.create(cvid='4321', cvurl='http://2.com',
                           name='Final Crisis', slug='final-crisis')

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
        resp = self.client.get(reverse('api:arc-list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK,
                         "REST token-auth failed")
        self.assertTrue(len(json.loads(resp.content)) == Arc.objects.count())

    def test_unauthorized_view_url(self):
        # Clear the credentials.
        self.client.credentials()
        resp = self.client.get(reverse('api:arc-list'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class GetSingleArcTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.hulk = Arc.objects.create(cvid='2345', cvurl='http://1.com',
                                      name='Hulk', slug='hulk')
        cls.crisis = Arc.objects.create(cvid='6789', cvurl='http://2.com',
                                        name='Infinite Crisis', slug='infinite-crisis')

    def setUp(self):
        self.email = 'tom@test.com'
        self.username = 'tom'
        self.password = 'test!thwip'
        self.user = User.objects.create_user(
            self.username, self.email, self.password)

        self.client = APIClient()
        self.token = Token.objects.get(user__username=self.username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_get_valid_single_arc(self):
        response = self.client.get(
            reverse('api:arc-detail', kwargs={'slug': self.hulk.slug}))
        arc = Arc.objects.get(slug=self.hulk.slug)
        serializer = ArcSerializer(arc)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_invalid_single_publisher(self):
        response = self.client.get(
            reverse('api:arc-detail', kwargs={'slug': 'civil-war'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthorized_view_url(self):
        # Clear the credentials.
        self.client.credentials()
        response = self.client.get(
            reverse('api:arc-detail', kwargs={'slug': self.hulk.slug}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
