from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_jwt import utils
from rest_framework_jwt.compat import get_user_model

from comics.models import Arc
from comics.serializers import ArcSerializer


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
        Arc.objects.create(cvid=1001, name='Blackest Night',
                           slug='blackest-night')
        Arc.objects.create(cvid=1002, name='Infinite Crisis',
                           slug='infinite-crisis')

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
        cls.black = Arc.objects.create(
            cvid=1001, name='Blackest Night', slug='blackest-night')
        cls.crisis = Arc.objects.create(
            cvid=1002, name='Infinite Crisis', slug='infinite-crisis')

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
