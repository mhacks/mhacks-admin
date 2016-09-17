from django.conf.urls import url

from push_notifications.api.rest_framework import APNSDeviceViewSet, GCMDeviceViewSet
from rest_framework_docs.views import DRFDocsView

from MHacks.v1.announcements import Announcements, Announcement
from MHacks.v1.auth import Authentication
from MHacks.v1.events import Events, Event
from MHacks.v1.locations import Locations, Location
from MHacks.v1.scan_event import ScanEvents, ScanEvent
from MHacks.v1.views import get_countdown, get_map, apple_pass_endpoint

urlpatterns = [
    # Authentication
    url(r'^login/$', Authentication.as_view(), name='api-login'),
    url(r'^announcements/(?P<id>[0-9A-Za-z_\-]+)$', Announcement.as_view()),
    url(r'^announcements/$', Announcements.as_view(), name='announcements'),
    url(r'^locations/(?P<id>[0-9A-Za-z_\-]+)$', Location.as_view()),
    url(r'^locations/$', Locations.as_view(), name='locations'),
    url(r'^events/(?P<id>[0-9A-Za-z_\-]+)$', Event.as_view()),
    url(r'^events/$', Events.as_view(), name='events'),
    url(r'^scan_event/(?P<id>[0-9A-Za-z_\-]+)', ScanEvent.as_view()),
    url(r'^scan_events', ScanEvents.as_view()),
    url(r'^countdown/$', get_countdown, name='countdown'),
    url(r'^map/$', get_map, name='maps'),
    url(r'^push_notifications/apns/$', APNSDeviceViewSet.as_view({'post': 'create', 'put': 'update'}), name='create_apns_device'),
    url(r'^push_notifications/gcm/$', GCMDeviceViewSet.as_view({'post': 'create', 'put': 'update'}), name='create_gcm_device'),
    url(r'^apple_pass/$', apple_pass_endpoint),
    url(r'^docs/$', DRFDocsView.as_view(template_name='docs.html'), name='docs'),
]
