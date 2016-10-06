from django.conf.urls import url, include
from MHacks.frontend.views import *
from django.views.generic.base import RedirectView

urlpatterns = [
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
    url(r'^live/$', live, name='mhacks-live'),
    url(r'^apply/$', application, name='mhacks-apply'),
    url(r'^thanks_for_registering/$', thanks_registering, name='mhacks-thanks-registering'),
    url(r'^applyMentor/$', apply_mentor, name='mhacks-applyMentor'),
    url(r'^registration/$', registration, name='mhacks-registration'),

    # Application reading
    url(r'^application_search/$', application_search, name='mhacks-applicationSearch'),
    url(r'^application_review/$', application_review, name='mhacks-applicationReview'),
    url(r'^update_applications/$', update_applications, name='mhacks-updateApplication'),

    # Sponsor portal
    url(r'^sponsor_portal', sponsor_portal, name='mhacks-sponsorPortal'),
    url(r'^sponsor_review', sponsor_review, name='mhacks-sponsorReview'),
    url(r'^resumes/(?P<filename>[\w\S]{0,256})/$', resumes, name='mhacks-resumes'),

    url(r'^explorer/', include('explorer.urls')),

    # Apple Wallet pass support
    url(r'^apple_pass.pkpass$', apple_pass, name='mhacks-apple-pass'),

    # Redirect all other endpoints to the homepage
    url(r'^.*/$', RedirectView.as_view(url='/', permanent=False), name='redirect-mhacks-home')
]
