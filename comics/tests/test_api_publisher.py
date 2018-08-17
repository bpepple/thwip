from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_jwt import utils
from rest_framework_jwt.compat import get_user_model

from comics.models import Publisher
from comics.serializers import PublisherSerializer


User = get_user_model()


def get_auth(user):
    payload = utils.jwt_payload_handler(user)
    token = utils.jwt_encode_handler(payload)
    auth = 'JWT {0}'.format(token)

    return auth


class GetAllPublisherTest(TestCase):

    def setUp(self):
        self.csrf_client = APIClient(enforce_csrf_checks=True)
        self.email = 'brian@test.com'
        self.username = 'brian'
        self.user = User.objects.create_user(self.username, self.email)

    @classmethod
    def setUpTestData(cls):
        Publisher.objects.create(name='DC Comics', slug='dc-comics')
        Publisher.objects.create(name='Marvel', slug='marvel')

    def test_view_url_accessible_by_name(self):
        resp = self.csrf_client.get(reverse('api:publisher-list'),
                                    HTTP_AUTHORIZATION=get_auth(self.user), format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


class GetSinglePublisherTest(TestCase):

    def setUp(self):
        self.csrf_client = APIClient(enforce_csrf_checks=True)
        self.email = 'brian@test.com'
        self.username = 'brian'
        self.user = User.objects.create_user(self.username, self.email)

    @classmethod
    def setUpTestData(cls):
        cls.dc = Publisher.objects.create(name='DC Comics', slug='dc-comics')
        cls.marvel = Publisher.objects.create(name='Marvel', slug='marvel')

    def test_get_valid_single_publisher(self):
        response = self.csrf_client.get(reverse('api:publisher-detail',
                                                kwargs={'slug': self.dc.slug}),
                                        HTTP_AUTHORIZATION=get_auth(self.user), format='json')
        publisher = Publisher.objects.get(slug=self.dc.slug)
        serializer = PublisherSerializer(publisher)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_absolute_url(self):
        reverse_url = reverse('api:publisher-detail',
                              kwargs={'slug': self.dc.slug})
        absolute_url = self.dc.get_absolute_url()
        self.assertEqual(reverse_url, absolute_url)

    def test_get_invalid_single_publisher(self):
        response = self.csrf_client.get(reverse('api:publisher-detail',
                                                kwargs={'slug': 'dark-horse'}),
                                        HTTP_AUTHORIZATION=get_auth(self.user), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
