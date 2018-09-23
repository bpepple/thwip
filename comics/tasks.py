from celery import shared_task

from .utils.comicimporter import ComicImporter


@shared_task
def import_comic_files_task():
    ci = ComicImporter()
    success = ci.import_comic_files()

    return success


@shared_task
def refresh_issue_task(cvid):
    ci = ComicImporter()
    success = ci.refreshIssueData(cvid)

    return success
