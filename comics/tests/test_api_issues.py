import json

from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.request import Request
from rest_framework.test import APIClient, APITestCase
from rest_framework.test import APIRequestFactory

from comics.models import Issue, Publisher, Series
from comics.serializers import IssueSerializer


issue_date = timezone.now().date()
mod_time = timezone.now()


class GetAllIssueTest(APITestCase):

    @classmethod
    def setUpTestData(cls):

        publisher_obj = Publisher.objects.create(
            name='DC Comics', slug='dc-comics')
        series_obj = Series.objects.create(
            cvid='1234', cvurl='http://1.com', name='Superman', slug='superman', publisher=publisher_obj)
        Issue.objects.create(cvid='1234', cvurl='http://1.com', slug='superman-1',
                             file='/home/a.cbz', mod_ts=mod_time, date=issue_date, number='1', series=series_obj)
        Issue.objects.create(cvid='4321', cvurl='http://2.com', slug='batman-1',
                             file='/home/b.cbz', mod_ts=mod_time, date=issue_date, number='1', series=series_obj)

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
        resp = self.client.get(reverse('api:issue-list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(len(json.loads(resp.content)) == Issue.objects.count())

    def test_unauthorized_view_url(self):
        # Clear the credentials.
        self.client.credentials()
        resp = self.client.get(reverse('api:issue-list'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class GetSingleIssueTest(APITestCase):

    @classmethod
    def setUpTestData(cls):

        factory = APIRequestFactory()
        request = factory.get('/')

        cls.serializer_context = {
            'request': Request(request),
        }

        publisher_obj = Publisher.objects.create(
            name='DC Comics', slug='dc-comics')
        series_obj = Series.objects.create(
            cvid='1234', cvurl='http://1.com', name='Superman', slug='superman', publisher=publisher_obj)
        cls.superman = Issue.objects.create(cvid='1234', cvurl='http://1.com', slug='superman-1',
                                            file='/home/a.cbz', mod_ts=mod_time, date=issue_date, number='1',
                                            series=series_obj)

    def setUp(self):
        self.email = 'tom@test.com'
        self.username = 'tom'
        self.password = 'test!thwip'
        self.user = User.objects.create_user(
            self.username, self.email, self.password)

        self.client = APIClient()
        self.token = Token.objects.get(user__username=self.username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_get_valid_single_issue(self):
        response = self.client.get(
            reverse('api:issue-detail', kwargs={'slug': self.superman.slug}))
        issue = Issue.objects.get(slug=self.superman.slug)
        serializer = IssueSerializer(issue, context=self.serializer_context)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_view_url(self):
        # Clear the credentials.
        self.client.credentials()
        response = self.client.get(
            reverse('api:issue-detail', kwargs={'slug': self.superman.slug}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
