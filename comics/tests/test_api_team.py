import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from comics.models import Team
from comics.serializers import TeamSerializer


class GetAllTeamsTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        Team.objects.create(cvid='1234', cvurl='http://1.com',
                            name='Teen Titans', slug='teen-titans')
        Team.objects.create(cvid='4321', cvurl='http://2.com',
                            name='The Avengers', slug='the-avengers')

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
        resp = self.client.get(reverse('api:team-list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(len(json.loads(resp.content)) == Team.objects.count())

    def test_unauthorized_view_url(self):
        # Clear the credentials.
        self.client.credentials()
        resp = self.client.get(reverse('api:team-list'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class GetSingleTeamTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.titans = Team.objects.create(
            cvid='1234', cvurl='http://1.com', name='Teen Titans', slug='teen-titans')
        cls.avengers = Team.objects.create(
            cvid='4321', cvurl='http://2.com', name='The Avengers', slug='the-avengers')

    def setUp(self):
        self.email = 'tom@test.com'
        self.username = 'tom'
        self.password = 'test!thwip'
        self.user = User.objects.create_user(
            self.username, self.email, self.password)

        self.client = APIClient()
        self.token = Token.objects.get(user__username=self.username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_get_valid_single_team(self):
        response = self.client.get(
            reverse('api:team-detail', kwargs={'slug': self.avengers.slug}))
        team = Team.objects.get(slug=self.avengers.slug)
        serializer = TeamSerializer(team)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_invalid_single_team(self):
        response = self.client.get(
            reverse('api:team-detail', kwargs={'slug': 'justice-league'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthorized_view_url(self):
        # Clear the credentials.
        self.client.credentials()
        response = self.client.get(
            reverse('api:team-detail', kwargs={'slug': self.avengers.slug}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
