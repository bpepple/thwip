from datetime import datetime
import os

from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
from django.utils.text import slugify

from comics.models import Issue, Settings, Publisher, Creator
from comics.tasks import import_comic_files_task


class TestTasks(TestCase):

    @classmethod
    def setUpTestData(cls):
        test_data_dir = settings.BASE_DIR + os.sep + 'comics/fixtures'
        cls. settings = Settings.objects.create(comics_directory=test_data_dir,
                                                api_key='27431e6787042105bd3e47e169a624521f89f3a4')

    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                       CELERY_ALWAYS_EAGER=True,
                       BROKER_BACKEND='memory')
    def test_import_comics_task(self):
        import_comic_files_task()

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

        # When the db is torn down after the test the images don't get
        # removed so let's do this clunky bit of code to handle it.
        people = ["Joe Gill", "Steve Ditko", "Jon D'Agostino"]
        slugified_names = []
        for creator in people:
            slugified_names.append(slugify(creator))

        for credit in slugified_names:
            c = Creator.objects.get(slug=credit)
            c.delete()

        publisher = Publisher.objects.get(slug='charlton')
        publisher.delete()
