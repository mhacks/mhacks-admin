from django.conf.urls import url
from rest_framework_docs.views import DRFDocsView
from announcements import Announcements, Announcement
from locations import Locations, Location
from events import Events, Event
from views import get_countdown, get_map
from auth import Authentication

urlpatterns = [
    # Authentication
    url(r'^login$', Authentication.as_view()),
    url(r'^announcements/(?P<id>[0-9A-Za-z_\-]+)$', Announcement.as_view()),
    url(r'^announcements/$', Announcements.as_view()),
    url(r'^locations/(?P<id>[0-9A-Za-z_\-]+)$', Location.as_view()),
    url(r'^locations/$', Locations.as_view()),
    url(r'^events/(?P<id>[0-9A-Za-z_\-]+)$', Event.as_view()),
    url(r'^events$', Events.as_view()),
    url(r'^countdown$', get_countdown),
    url(r'^map$', get_map),
    url(r'^docs/$', DRFDocsView.as_view(template_name='docs.html'), name='docs'),
]
