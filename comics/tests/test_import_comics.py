from datetime import datetime
import os

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_jwt import utils
from rest_framework_jwt.compat import get_user_model

from comics.models import (Settings, Issue, Publisher,
                           Creator, Role, Series)
from comics.utils.comicimporter import ComicImporter


User = get_user_model()


class TestImportComics(TestCase):

    def setUp(self):
        self.csrf_client = APIClient(enforce_csrf_checks=True)
        self.email = 'brian@test.com'
        self.username = 'brian'
        self.user = User.objects.create_user(self.username, self.email)

    @classmethod
    def setUpTestData(cls):
        issue_date = timezone.now().date()
        mod_time = timezone.now()

        cls.pub_cvid = 10
        cls.ser_cvid = 796
        cls.creator_cvid = 41468
        cls.issue_cvid = 286879

        cls.dc = Publisher.objects.create(
            cvid=cls.pub_cvid, name='DC Comics', slug='dc-comics')
        cls.bat = Series.objects.create(
            cvid=cls.ser_cvid, name='Batman', slug='batman', publisher=cls.dc)
        cls.creator = Creator.objects.create(cvid=cls.creator_cvid, name='Ed Brubaker',
                                             slug='ed-brubaker')
        cls.issue = Issue.objects.create(series=cls.bat, cvid=cls.issue_cvid,
                                         slug='batman-713', mod_ts=mod_time, date=issue_date,
                                         number='713')

        test_data_dir = settings.BASE_DIR + os.sep + 'comics/fixtures'
        cls. settings = Settings.objects.create(comics_directory=test_data_dir,
                                                api_key='27431e6787042105bd3e47e169a624521f89f3a4')

    def tearDown(self):
        # Clean up all the images that were downloaded.
        for publisher in Publisher.objects.all():
            publisher.delete()

        for creator in Creator.objects.all():
            creator.delete()

    def test_settings_str(self):
        self.assertEqual(self.settings.__str__(), 'Settings')

    def test_refresh_publisher(self):
        ci = ComicImporter()
        ci.refreshPublisherData(self.pub_cvid)
        self.dc.refresh_from_db()

        self.assertTrue(self.dc.desc)

    def test_refresh_series(self):
        ci = ComicImporter()
        ci.refreshSeriesData(self.ser_cvid)
        self.bat.refresh_from_db()

        self.assertTrue(self.bat.desc)
        self.assertEqual(self.bat.year, 1940)

    def test_refresh_creator(self):
        ci = ComicImporter()
        ci.refreshCreatorData(self.creator_cvid)
        self.creator.refresh_from_db()

        self.assertTrue(self.creator.desc)

    def test_refresh_issue(self):
        ci = ComicImporter()
        ci.refreshIssueData(self.issue_cvid)
        self.issue.refresh_from_db()

        self.assertTrue(self.issue.desc)
        self.assertTrue(self.issue.name)

    def test_import_comic(self):
        ci = ComicImporter()
        ci.import_comic_files()

        cover_date = datetime.strptime('December 01, 1965', '%B %d, %Y')
        issue = Issue.objects.get(cvid=8192)

        # Change the issue leaf so we can check read_percent.
        leaf = issue.leaf
        issue.leaf = leaf + 2
        issue.save()

        self.assertEqual(str(issue), 'Captain Atom #078')
        self.assertEqual(issue.percent_read, 12)
        self.assertEqual(issue.date, datetime.date(cover_date))
        self.assertTrue(issue.image)

    def test_get_page(self):
        ci = ComicImporter()
        ci.import_comic_files()

        role = Role.objects.get(id=1)
        issue = Issue.objects.get(cvid=8192)

        payload = utils.jwt_payload_handler(self.user)
        token = utils.jwt_encode_handler(payload)
        auth = 'JWT {0}'.format(token)
        resp = self.csrf_client.get(reverse('api:issue-get-page',
                                            kwargs={'slug': issue.slug, 'page': 1}),
                                    HTTP_AUTHORIZATION=auth, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Check the Role Models str()
        self.assertEqual(role.__str__(), role.name)
