from django.core.management.base import BaseCommand
from push_notifications.models import APNSDevice, GCMDevice
from push_notifications.apns import APNSDataOverflow, apns_send_bulk_message
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
            print(announcement)
            if announcement.category and (announcement.category & 1 == 0):
                apns_devices = APNSDevice.objects.all().filter(active=True).extra(where=['CAST(name as INTEGER) & %s != 0'],
                                                                                  params=str(announcement.category))
                gcm_devices = GCMDevice.objects.all().filter(active=True).extra(where=['CAST(name as INTEGER) & %s != 0'],
                                                                                params=str(announcement.category))
            else:
                apns_devices = APNSDevice.objects.all().filter(active=True)
                gcm_devices = GCMDevice.objects.all().filter(active=True)

            print(len(apns_devices))
            print(len(gcm_devices))
            for i in range(0, len(apns_devices), 50):
                from datetime import time
                try:
                    reg_ids = map(lambda d: d.registration_id, apns_devices[i:i + 50])
                    apns_send_bulk_message(registration_ids=reg_ids, alert=announcement.info, sound='default',
                                           extra={"category": announcement.category, "title": announcement.title})
                    time.sleep(0.5)
                except APNSDataOverflow:
                    pass
            gcm_devices.send_message(announcement.info)
