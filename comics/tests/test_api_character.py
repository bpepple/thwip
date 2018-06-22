from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from comics.models import Character
from comics.serializers import CharacterSerializer


class GetAllCharactersTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        for character in range(105):
            Character.objects.create(
                name='Character %s' % character,
                slug='character-%s' % character,
                cvid=character)

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
        resp = self.client.get(reverse('api:character-list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_unauthorized_view_url(self):
        # Clear the credentials.
        self.client.credentials()
        resp = self.client.get(reverse('api:character-list'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class GetSingleCharacterTest(APITestCase):

    @classmethod
    def setUpTestData(cls):

        cls.superman = Character.objects.create(
            cvid='1234', cvurl='http://1.com', name='Superman', slug='superman')
        cls.batman = Character.objects.create(
            cvid='4321', cvurl='http://2.com', name='Batman', slug='batman')

    def setUp(self):
        self.email = 'tom@test.com'
        self.username = 'tom'
        self.password = 'test!thwip'
        self.user = User.objects.create_user(
            self.username, self.email, self.password)

        self.client = APIClient()
        self.token = Token.objects.get(user__username=self.username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_get_valid_single_character(self):
        response = self.client.get(
            reverse('api:character-detail', kwargs={'slug': self.batman.slug}))
        character = Character.objects.get(slug=self.batman.slug)
        serializer = CharacterSerializer(character)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_invalid_single_character(self):
        response = self.client.get(
            reverse('api:character-detail', kwargs={'slug': 'wonder-woman'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthorized_view_url(self):
        # Clear the credentials.
        self.client.credentials()
        response = self.client.get(
            reverse('api:character-detail', kwargs={'slug': self.batman.slug}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
