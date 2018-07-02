import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from comics.models import Creator
from comics.serializers import CreatorSerializer


class GetAllCreatorsTest(APITestCase):

    @classmethod
    def setUpTestData(cls):

        Creator.objects.create(
            cvid='1234', cvurl='http://1.com', name='John Byrne', slug='john-byrne')
        Creator.objects.create(cvid='4321', cvurl='http://2.com',
                               name='Walter Simonson', slug='walter-simonson')

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
        resp = self.client.get(reverse('api:creator-list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(len(json.loads(resp.content))
                        == Creator.objects.count())

    def test_unauthorized_view_url(self):
        # Clear the credentials.
        self.client.credentials()
        resp = self.client.get(reverse('api:creator-list'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class GetSingleCreatorTest(APITestCase):

    @classmethod
    def setUpTestData(cls):

        cls.john = Creator.objects.create(
            cvid='1234', cvurl='http://1.com', name='John Byrne', slug='john-byrne')
        cls.walter = Creator.objects.create(
            cvid='4321', cvurl='http://2.com', name='Walter Simonson', slug='walter-simonson')

    def setUp(self):
        self.email = 'tom@test.com'
        self.username = 'tom'
        self.password = 'test!thwip'
        self.user = User.objects.create_user(
            self.username, self.email, self.password)

        self.client = APIClient()
        self.token = Token.objects.get(user__username=self.username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_get_valid_single_creator(self):
        response = self.client.get(
            reverse('api:creator-detail', kwargs={'slug': self.walter.slug}))
        creator = Creator.objects.get(slug=self.walter.slug)
        serializer = CreatorSerializer(creator)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_invalid_single_creator(self):
        response = self.client.get(
            reverse('api:creator-detail', kwargs={'slug': 'art-adams'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthorized_view_url(self):
        # Clear the credentials.
        self.client.credentials()
        response = self.client.get(
            reverse('api:creator-detail', kwargs={'slug': self.walter.slug}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
