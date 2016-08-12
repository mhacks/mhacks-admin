from django.conf.urls import url
from MHacks.frontend.views import *
from django.views.generic.base import RedirectView


urlpatterns = [
    url(r'^$', index, name='mhacks-home'),
    url(r'^.*$', RedirectView.as_view(url='/', permanent=False), name='redirect-mhacks-home'),  # Redirect everything to root page

    # Authentication
    url(r'^register/$', register, name='mhacks-register'),
    url(r'^validate/(?P<uid>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        validate_email, name='mhacks-validate'),
    url(r'^send_verify_email/(?P<user_pk>[0-9A-Za-z_\-]+)/$', request_verification_email,
        name='mhacks-verification-email'),
    url(r'^login/$', login, name='mhacks-login'),
    url(r'^logout/$', logout, name='mhacks-logout'),
    url(r'^reset/$', reset_password, name='mhacks-reset_password'),
    url(r'^update_password/(?P<uid>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        update_password, name='mhacks-update_password'),

    # Content
    url(r'^dashboard/$', dashboard, name='mhacks-dashboard'),
    url(r'^live/$', live, name='mhacks-live'),
    url(r'^apply/$', application, name='mhacks-apply'),
    url(r'^applyMentor/$', applyMentor, name='mhacks-applyMentor')
]
