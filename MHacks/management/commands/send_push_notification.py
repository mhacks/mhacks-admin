from django.core.management.base import BaseCommand
from push_notifications.models import APNSDevice, GCMDevice
from push_notifications.apns import APNSDataOverflow
from MHacks.models import Announcement


class Command(BaseCommand):
    help = 'Run for sending push notifications for all announcements before now'

    def handle(self, *args, **options):
        import pytz
        from datetime import datetime
        announcements = Announcement.objects.all().filter(sent=False, broadcast_at__lte=datetime.now(pytz.utc))
        for announcement in announcements:
            announcement.sent = True
            announcement.save()  # Save immediately so even if this takes time to run, we won't have duplicate pushes
            if announcement.category and (announcement.category & 1 == 0):
                apns_devices = APNSDevice.objects.all().filter(active=True).extra(where=['CAST(name as INTEGER) & %s != 0'],
                                                                                  params=str(announcement.category))
                gcm_devices = GCMDevice.objects.all().filter(active=True).extra(where=['CAST(name as INTEGER) & %s != 0'],
                                                                                params=str(announcement.category))
            else:
                apns_devices = APNSDevice.objects.all().filter(active=True)
                gcm_devices = GCMDevice.objects.all().filter(active=True)

            print(apns_devices)
            print(gcm_devices)

            # try:
            #     aps_data = {"alert": {"body": announcement.info, "title": announcement.title},
            #                 "sound": "default"}
            #     apns_devices.send_message(announcement.info, sound='default', extra={"category": announcement.category, "title": announcement.title})
            # except APNSDataOverflow:
            #     apns_devices.send_message(announcement.title)
            # gcm_devices.send_message(announcement.info)
