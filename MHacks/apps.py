from django.apps import AppConfig
from django.db.models.signals import post_migrate

from MHacks.utils import add_permissions


class MhacksConfig(AppConfig):
    name = 'MHacks'

    def ready(self):
        post_migrate.connect(add_permissions, sender=self)
