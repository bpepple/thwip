from celery import shared_task

from .utils.comicimporter import ComicImporter


@shared_task
def import_comic_files_task():
    ci = ComicImporter()
    success = ci.import_comic_files()

    return success
