from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory, APITestCase

from comics.models import Issue, Publisher, Series
from comics.serializers import IssueSerializer, ReaderSerializer


issue_date = timezone.now().date()
mod_time = timezone.now()


class GetAllIssueTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        publisher_obj = Publisher.objects.create(
            name='DC Comics', slug='dc-comics')
        series_obj = Series.objects.create(
            cvid='1234', cvurl='http://1.com', name='Superman', slug='superman', publisher=publisher_obj)
        Issue.objects.create(cvid='1234', cvurl='http://1.com', slug='superman-1', page_count='21',
                             file='/home/a.cbz', mod_ts=mod_time, date=issue_date, number='1', series=series_obj)
        Issue.objects.create(cvid='4321', cvurl='http://2.com', slug='batman-1',
                             file='/home/b.cbz', mod_ts=mod_time, date=issue_date, number='1', series=series_obj)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('api:issue-list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


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
                                            file='/home/a.cbz', mod_ts=mod_time, date=issue_date, number='1', series=series_obj)

    def test_get_valid_single_issue(self):
        response = self.client.get(
            reverse('api:issue-detail', kwargs={'slug': self.superman.slug}))
        issue = Issue.objects.get(slug=self.superman.slug)
        serializer = IssueSerializer(issue, context=self.serializer_context)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_issue_reader(self):
        response = self.client.get(
            reverse('api:issue-reader', kwargs={'slug': self.superman.slug}))
        issue = Issue.objects.get(slug=self.superman.slug)
        serializer = ReaderSerializer(issue, context=self.serializer_context)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_issue_update_values(self):
        # Let's change the leaf to 10, and change the read status to Read (2).
        change_values = {'leaf': 10, 'status': 2}
        response = self.client.put(reverse('api:issue-detail', kwargs={'slug': self.superman.slug}),
                                   change_values, format='json')
        issue = Issue.objects.get(slug=self.superman.slug)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(10, issue.leaf)
        self.assertEqual(2, issue.status)

    def test_get_invalid_single_issue(self):
        response = self.client.get(
            reverse('api:issue-detail', kwargs={'slug': 'airboy-001'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
