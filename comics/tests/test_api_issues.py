from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory, APITestCase, APIClient
from rest_framework_jwt import utils
from rest_framework_jwt.compat import get_user_model

from comics.models import Arc, Issue, Publisher, Series
from comics.serializers import IssueSerializer, ReaderSerializer


issue_date = timezone.now().date()
mod_time = timezone.now()

User = get_user_model()


def get_auth(user):
    payload = utils.jwt_payload_handler(user)
    token = utils.jwt_encode_handler(payload)
    auth = 'JWT {0}'.format(token)

    return auth


class GetAllIssueTest(APITestCase):

    def setUp(self):
        self.csrf_client = APIClient(enforce_csrf_checks=True)
        self.email = 'brian@test.com'
        self.username = 'brian'
        self.user = User.objects.create_user(self.username, self.email)

    @classmethod
    def setUpTestData(cls):
        publisher_obj = Publisher.objects.create(
            name='DC Comics', slug='dc-comics')
        cls.blackest = Arc.objects.create(
            cvid=1001, name='Blackest Night', slug='blackest-night')
        cls.superman = Series.objects.create(cvid='1234', cvurl='http://1.com', name='Superman',
                                             slug='superman', publisher=publisher_obj)
        issue1_obj = Issue.objects.create(cvid='1234', cvurl='http://1.com', slug='superman-1', page_count='21',
                                          file='/home/a.cbz', mod_ts=mod_time, date=issue_date, number='1', series=cls.superman)
        issue2_obj = Issue.objects.create(cvid='4321', cvurl='http://2.com', slug='batman-1',
                                          file='/home/b.cbz', mod_ts=mod_time, date=issue_date, number='1', series=cls.superman)

        issue1_obj.arcs.set([cls.blackest])
        issue2_obj.arcs.set([cls.blackest])

    def test_view_url_accessible_by_name(self):
        resp = self.csrf_client.get(reverse('api:issue-list'),
                                    HTTP_AUTHORIZATION=get_auth(self.user),
                                    format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_recent_issue_list(self):
        resp = self.csrf_client.get(reverse('api:issue-recent'),
                                    HTTP_AUTHORIZATION=get_auth(self.user),
                                    format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_series_issue_list(self):
        resp = self.csrf_client.get(reverse('api:series-issue-list',
                                            kwargs={'slug': self.superman.slug}),
                                    HTTP_AUTHORIZATION=get_auth(self.user), format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_arc_issue_list(self):
        resp = self.csrf_client.get(reverse('api:arc-issue-list',
                                            kwargs={'slug': self.blackest.slug}),
                                    HTTP_AUTHORIZATION=get_auth(self.user), format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


class GetSingleIssueTest(APITestCase):

    def setUp(self):
        self.csrf_client = APIClient(enforce_csrf_checks=True)
        self.email = 'brian@test.com'
        self.username = 'brian'
        self.user = User.objects.create_user(self.username, self.email)

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
        response = self.csrf_client.get(reverse('api:issue-detail',
                                                kwargs={'slug': self.superman.slug}),
                                        HTTP_AUTHORIZATION=get_auth(self.user), format='json')
        issue = Issue.objects.get(slug=self.superman.slug)
        serializer = IssueSerializer(issue, context=self.serializer_context)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_absolute_url(self):
        reverse_url = reverse('api:issue-detail',
                              kwargs={'slug': self.superman.slug})
        absolute_url = self.superman.get_absolute_url()
        self.assertEqual(reverse_url, absolute_url)

    def test_issue_reader(self):
        response = self.csrf_client.get(reverse('api:issue-reader',
                                                kwargs={'slug': self.superman.slug}),
                                        HTTP_AUTHORIZATION=get_auth(self.user), format='json')
        issue = Issue.objects.get(slug=self.superman.slug)
        serializer = ReaderSerializer(issue, context=self.serializer_context)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_issue_update_values(self):
        # Let's change the leaf to 10, and change the read status to Read (2).
        change_values = {'leaf': 10, 'status': 2}
        response = self.csrf_client.put(reverse('api:issue-detail',
                                                kwargs={'slug': self.superman.slug}),
                                        change_values,
                                        HTTP_AUTHORIZATION=get_auth(self.user),
                                        format='json')
        issue = Issue.objects.get(slug=self.superman.slug)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(10, issue.leaf)
        self.assertEqual(2, issue.status)

    def test_get_invalid_single_issue(self):
        response = self.csrf_client.get(reverse('api:issue-detail',
                                                kwargs={'slug': 'airboy-001'}),
                                        HTTP_AUTHORIZATION=get_auth(self.user), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
