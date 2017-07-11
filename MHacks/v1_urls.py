from django.conf.urls import url
from rest_framework_docs.views import DRFDocsView

from MHacks.events import EventListAPIView, EventAPIView
from MHacks.locations import LocationListAPIView, LocationAPIView
from MHacks.scan_events import ScanEventListAPIView, ScanEventAPIView
from views import get_countdown
from announcements import AnnouncementListAPIView, AnnouncementAPIView
from authentication import AuthenticationAPIView
from floors import FloorListAPIView, FloorAPIView
from push_notifications import APNSTokenView, GCMTokenView
from scan_events import perform_scan
from users import update_user_profile

urlpatterns = [
    # Authentication
    url(r'^login/$', AuthenticationAPIView.as_view(), name='api-login'),
    url(r'^announcements/(?P<id>[0-9A-Za-z_\-]+)$', AnnouncementAPIView.as_view()),
    url(r'^announcements/$', AnnouncementListAPIView.as_view(), name='announcements'),
    url(r'^locations/(?P<id>[0-9A-Za-z_\-]+)$', LocationAPIView.as_view()),
    url(r'^locations/$', LocationListAPIView.as_view(), name='locations'),
    url(r'^events/(?P<id>[0-9A-Za-z_\-]+)$', EventAPIView.as_view()),
    url(r'^events/$', EventListAPIView.as_view(), name='events'),
    url(r'^floors/(?P<id>[0-9A-Za-z_\-]+)', FloorAPIView.as_view()),
    url(r'^floors', FloorListAPIView.as_view(), name='floors'),
    url(r'^scan_events/(?P<id>[0-9A-Za-z_\-]+)', ScanEventAPIView.as_view()),
    url(r'^scan_events', ScanEventListAPIView.as_view(), name='scan_events'),
    url(r'^perform_scan/', perform_scan, name='perform_scan'),
    url(r'^countdown/$', get_countdown, name='countdown'),
    url(r'^profile/$', update_user_profile, name='profile'),
    url(r'^push_notifications/apns/$', APNSTokenView.as_view(), name='create_apns_device'),
    url(r'^push_notifications/gcm/$', GCMTokenView.as_view(), name='create_gcm_device'),
    url(r'^docs/$', DRFDocsView.as_view(template_name='docs.html'), name='docs'),
]
