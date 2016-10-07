from django.conf.urls import url
from rest_framework_docs.views import DRFDocsView

from MHacks.v1.announcements import Announcements, Announcement
from MHacks.v1.auth import Authentication
from MHacks.v1.events import Events, Event
from MHacks.v1.floors import Floors, Floor
from MHacks.v1.locations import Locations, Location
from MHacks.v1.push_notification_views import APNSTokenView, GCMTokenView
from MHacks.v1.scan_event import ScanEvents, ScanEvent
from MHacks.v1.views import get_countdown, apple_pass_endpoint, update_user_profile, perform_scan

urlpatterns = [
    # Authentication
    url(r'^login/$', Authentication.as_view(), name='api-login'),
    url(r'^announcements/(?P<id>[0-9A-Za-z_\-]+)$', Announcement.as_view()),
    url(r'^announcements/$', Announcements.as_view(), name='announcements'),
    url(r'^locations/(?P<id>[0-9A-Za-z_\-]+)$', Location.as_view()),
    url(r'^locations/$', Locations.as_view(), name='locations'),
    url(r'^events/(?P<id>[0-9A-Za-z_\-]+)$', Event.as_view()),
    url(r'^events/$', Events.as_view(), name='events'),
    url(r'^floors/(?P<id>[0-9A-Za-z_\-]+)', Floor.as_view()),
    url(r'^floors', Floors.as_view(), name='floors'),
    url(r'^scan_events/(?P<id>[0-9A-Za-z_\-]+)', ScanEvent.as_view()),
    url(r'^scan_events', ScanEvents.as_view(), name='scan_events'),
    url(r'^perform_scan/', perform_scan, name='perform_scan'),
    url(r'^countdown/$', get_countdown, name='countdown'),
    url(r'^profile/$', update_user_profile, name='profile'),
    url(r'^push_notifications/apns/$', APNSTokenView.as_view(), name='create_apns_device'),
    url(r'^push_notifications/gcm/$', GCMTokenView.as_view(), name='create_gcm_device'),
    url(r'^apple_pass/$', apple_pass_endpoint, name='apple_pass_endpoint'),
    url(r'^docs/$', DRFDocsView.as_view(template_name='docs.html'), name='docs'),
]
