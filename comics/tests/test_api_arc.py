import os

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_jwt import utils
from rest_framework_jwt.compat import get_user_model

from comics.models import Arc, Issue, Publisher, Series, Settings
from comics.serializers import ArcSerializer
from comics.tasks import refresh_issue_task, refresh_arc_task


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
        test_data_dir = settings.BASE_DIR + os.sep + 'comics/fixtures'
        cls. settings = Settings.objects.create(comics_directory=test_data_dir,
                                                api_key='27431e6787042105bd3e47e169a624521f89f3a4')
        publisher_obj = Publisher.objects.create(
            cvid=10, name='DC Comics', slug='dc-comics')
        cls.black = Arc.objects.create(
            cvid=55766, name='Blackest Night', slug='blackest-night')
        cls.crisis = Arc.objects.create(
            cvid=40765, name='Infinite Crisis', slug='infinite-crisis')
        cls.superman = Series.objects.create(cvid=3816,
                                             cvurl='https://comicvine.gamespot.com/superman/4050-3816/',
                                             name='Superman',
                                             slug='superman',
                                             publisher=publisher_obj)
        cls.superman224 = Issue.objects.create(cvid=119106,
                                               cvurl='https://comicvine.gamespot.com/superman-224-focus/4000-119106/',
                                               slug='superman-224', page_count='21', file='/home/a.cbz',
                                               mod_ts=mod_time, date=issue_date, number='224', series=cls.superman)
        cls.superman225 = Issue.objects.create(cvid=107883,
                                               cvurl='https://comicvine.gamespot.com/superman-225-to-be-a-hero/4000-107883/',
                                               slug='superman-225', file='/home/b.cbz', mod_ts=mod_time,
                                               date=issue_date, number='225', series=cls.superman)

        cls.superman224.arcs.set([cls.crisis])
        cls.superman225.arcs.set([cls.crisis])

    def test_get_valid_single_arc(self):
        response = self.csrf_client.get(reverse('api:arc-detail',
                                                kwargs={'slug': self.crisis.slug}),
                                        HTTP_AUTHORIZATION=get_auth(self.user), format='json')
        arc = Arc.objects.get(slug=self.crisis.slug)
        serializer = ArcSerializer(arc)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_absolute_url(self):
        reverse_url = reverse('api:arc-detail',
                              kwargs={'slug': self.crisis.slug})
        absolute_url = self.crisis.get_absolute_url()
        self.assertEqual(reverse_url, absolute_url)

    def test_get_invalid_single_arc(self):
        response = self.csrf_client.get(reverse('api:arc-detail',
                                                kwargs={'slug': 'flashpoint'}),
                                        HTTP_AUTHORIZATION=get_auth(self.user), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # TODO: The following tasks test should probably be moved to their own
    # file.

    def test_refresh_issue_task(self):
        refresh_issue_task(self.superman225.cvid)
        # Refresh the issue object.
        self.superman225.refresh_from_db()
        # Clean up the image.
        if (self.superman225.image):
            self.superman225.image.delete()

        self.assertEqual(self.superman225.name, 'To Be a Hero')

    def test_refresh_arc_task(self):
        # This may change at Comic Vine so it's a bit fragile but for now let's
        # us it.
        desc = "In the chaos ensuing after the unleashing of the OMACs on Earth, the Spectre's vendetta against magic, and "
        desc += "the Rann-Thanagar War, four beings decide to try and save the universe: Superman and Lois Lane of Earth-Two, "
        desc += "Superboy of Earth-Prime, and Alexander Luthor of Earth-Three. What resulted was the *Infinite Crisis.*"
        refresh_arc_task(self.crisis.cvid)
        self.crisis.refresh_from_db()
        # Clean up the image
        if (self.crisis.image):
            self.crisis.image.delete()

        self.assertEqual(self.crisis.desc, desc)
