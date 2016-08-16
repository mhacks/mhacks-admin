# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$xo%i8vi+d624)&5)msxs3)s5tunm3dj9#n+fqn*zl%am%==!%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': 'localhost',
        'NAME': 'mhacks',
        'CONN_MAX_AGE': None,  # Unlimited
        'USE_TZ': True,
    }
}

# This is for push_notifications
PUSH_NOTIFICATIONS_SETTINGS = {
    "GCM_API_KEY": "",
    "APNS_CERTIFICATE": ""
}

# Security
# https://docs.djangoproject.com/en/1.9/topics/security/#ssl-https
# TODO: Use True for all of these for HTTPS on production settings
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

EMAIL_HOST_USER = 'hackathon@umich.edu'
# EMAIL_HOST_PASSWORD = '' for production
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Remove this line from production
EMAIL_HOST = 'localhost'

MANDRILL_API_KEY = 'THIS IS A DUMMY API KEY'
MAILCHIMP_API_KEY = 'THIS IS A DUMMY MAILCHIMP KEY'  # Use API KEY for MAILCHIMP on production
MAILCHIMP_INTEREST_LIST = 'https://us6.api.mailchimp.com/3.0/lists'  # Fill with actual list URL on production
# ^ This is for the blackout interest link

