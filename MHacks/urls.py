from django.conf.urls import url, include
from django.views.generic.base import RedirectView

from MHacks.views import *
from views import index

urlpatterns = [
    # Blackout
    # url(r'^$', blackout, name='mhacks-blackout'),
    # url(r'^.*/$', RedirectView.as_view(url='/', permanent=False), name='redirect-mhacks-blackout'),

    # Homepage
    url(r'^$', index, name='mhacks-home'),

    # Authentication
    url(r'^register/$', register, name='mhacks-register'),
    url(r'^validate/(?P<uid>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        validate_email, name='mhacks-validate'),
    url(r'^send_verify_email/(?P<user_pk>[0-9A-Za-z_\-]+)/$', request_verification_email,
        name='mhacks-verification-email'),
    url(r'^login/$', login, name='mhacks-login'),
    url(r'^logout/$', logout, name='mhacks-logout'),
    url(r'^reset/$', reset_password, name='mhacks-reset_password'),
    url(r'^password_reset_sent/$', password_reset_sent, name='mhacks-password_reset_sent'),
    url(r'^update_password/(?P<uid>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        update_password, name='mhacks-update_password'),

    # Content
    url(r'^dashboard/$', dashboard, name='mhacks-dashboard'),
    url(r'^thanks_for_registering/$', thanks_registering, name='mhacks-thanks-registering'),

    # Admin only
    url(r'^explorer/', include('explorer.urls')),

    url(r'^apple-app-site-association', apple_site_association),

    # Redirect all other endpoints to the homepage
    url(r'^.*/$', RedirectView.as_view(url='/', permanent=False), name='redirect-mhacks-home')
]
