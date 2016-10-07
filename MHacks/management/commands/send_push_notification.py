from django.core.management.base import BaseCommand
from push_notifications.models import APNSDevice
from MHacks.models import Announcement
from datetime import datetime


class Command(BaseCommand):
    help = 'Run for push notifications'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        import pytz
        announcements = Announcement.objects.all().filter(sent=False, broadcast_at__lte=datetime.now(pytz.utc))
        for announcement in announcements:
            APNSDevice.objects.all().filter(active=True).send_message(announcement.info)
