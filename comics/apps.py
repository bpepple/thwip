from django.apps import AppConfig
from django.db.models.signals import pre_delete

from comics.signals import (pre_delete_image, pre_delete_issue)


class ComicsConfig(AppConfig):
    name = 'comics'

    def ready(self):
        arc = self.get_model('Arc')
        pre_delete.connect(pre_delete_image, sender=arc,
                           dispatch_uid='pre_delete_arc')

        creator = self.get_model('Creator')
        pre_delete.connect(pre_delete_image, sender=creator,
                           dispatch_uid='pre_delete_creator')

        publisher = self.get_model('Publisher')
        pre_delete.connect(pre_delete_image, sender=publisher,
                           dispatch_uid='pre_delete_publisher')

        issue = self.get_model('Issue')
        pre_delete.connect(pre_delete_issue, sender=issue,
                           dispatch_uid='pre_delete_issue')
