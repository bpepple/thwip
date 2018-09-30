from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_jwt import utils
from rest_framework_jwt.compat import get_user_model

from comics.models import Arc, Issue, Publisher, Series
from comics.serializers import ArcSerializer
from django.utils import timezone

issue_date = timezone.now().date()
mod_time = timezone.now()

User = get_user_model()


def get_auth(user):
    payload = utils.jwt_payload_handler(user)
    token = utils.jwt_encode_handler(payload)
    auth = 'JWT {0}'.format(token)

    return auth


class GetAllArcTest(TestCase):

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
        Arc.objects.create(cvid=1002, name='Infinite Crisis',
                           slug='infinite-crisis')
        cls.superman = Series.objects.create(cvid='1234', cvurl='http://1.com', name='Superman',
                                             slug='superman', publisher=publisher_obj)
        issue1_obj = Issue.objects.create(cvid='1234', cvurl='http://1.com', slug='superman-1', page_count=21, leaf=20,
                                          file='/home/a.cbz', mod_ts=mod_time, date=issue_date, number='1', series=cls.superman)
        issue2_obj = Issue.objects.create(cvid='4321', cvurl='http://2.com', slug='batman-1',  page_count='21',
                                          file='/home/b.cbz', mod_ts=mod_time, date=issue_date, number='1', series=cls.superman)

        issue1_obj.arcs.set([cls.blackest])
        issue2_obj.arcs.set([cls.blackest])

    def test_view_url_accessible_by_name(self):
        resp = self.csrf_client.get(reverse('api:arc-list'),
                                    HTTP_AUTHORIZATION=get_auth(self.user), format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


class GetSingleArcTest(TestCase):

    def setUp(self):
        self.csrf_client = APIClient(enforce_csrf_checks=True)
        self.email = 'brian@test.com'
        self.username = 'brian'
        self.user = User.objects.create_user(self.username, self.email)

    @classmethod
    def setUpTestData(cls):
        publisher_obj = Publisher.objects.create(
            name='DC Comics', slug='dc-comics')
        cls.black = Arc.objects.create(
            cvid=1001, name='Blackest Night', slug='blackest-night')
        cls.crisis = Arc.objects.create(
            cvid=1002, name='Infinite Crisis', slug='infinite-crisis')
        cls.superman = Series.objects.create(cvid='1234', cvurl='http://1.com', name='Superman',
                                             slug='superman', publisher=publisher_obj)
        issue1_obj = Issue.objects.create(cvid='1234', cvurl='http://1.com', slug='superman-1', page_count='21',
                                          file='/home/a.cbz', mod_ts=mod_time, date=issue_date, number='1', series=cls.superman)
        issue2_obj = Issue.objects.create(cvid='4321', cvurl='http://2.com', slug='batman-1',
                                          file='/home/b.cbz', mod_ts=mod_time, date=issue_date, number='1', series=cls.superman)

        issue1_obj.arcs.set([cls.black])
        issue2_obj.arcs.set([cls.black])

    def test_get_valid_single_arc(self):
        response = self.csrf_client.get(reverse('api:arc-detail',
                                                kwargs={'slug': self.black.slug}),
                                        HTTP_AUTHORIZATION=get_auth(self.user), format='json')
        arc = Arc.objects.get(slug=self.black.slug)
        serializer = ArcSerializer(arc)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_absolute_url(self):
        reverse_url = reverse('api:arc-detail',
                              kwargs={'slug': self.black.slug})
        absolute_url = self.black.get_absolute_url()
        self.assertEqual(reverse_url, absolute_url)

    def test_get_invalid_single_arc(self):
        response = self.csrf_client.get(reverse('api:arc-detail',
                                                kwargs={'slug': 'flashpoint'}),
                                        HTTP_AUTHORIZATION=get_auth(self.user), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
