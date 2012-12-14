"""
GENTRY SETTINGS
---------------
"""

from graphite.settings import *
from sentry.conf.server import *


import os

DEBUG = True

CONF_ROOT = os.path.dirname(__file__)

# Change this to the path where the database file will be stored.
DATA_ROOT = ''

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',     # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(DATA_ROOT, 'gentry.db'),   # Or path to database file if using sqlite3.
        'USER': '',                                 # Not used with sqlite3.
        'PASSWORD': '',                             # Not used with sqlite3.
        'HOST': '',                                 # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                                 # Set to empty string for default. Not used with sqlite3.
    }
}

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''


# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'sentry.middleware.SentryMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.gzip.GZipMiddleware',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'm$3q%n4q3#khc5nih2)83$c67d09&amp;iv6*&amp;kw$x#8l37--ye-g9'

ROOT_URLCONF = 'gentry.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'gentry.wsgi.application'

INSTALLED_APPS = (
    'gentry',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',

    # Sentry
    'crispy_forms',
    'djcelery',
    'gunicorn',
    'kombu.transport.django',
    'raven.contrib.django',
    'sentry',
    'sentry.plugins.sentry_mail',
    'sentry.plugins.sentry_servers',
    'sentry.plugins.sentry_urls',
    'sentry.plugins.sentry_user_emails',
    'sentry.plugins.sentry_useragents',
    'social_auth',
    'south',
    'django_social_auth_trello',

    # Graphite
    'graphite.metrics',
    'graphite.render',
    'graphite.cli',
    'graphite.browser',
    'graphite.composer',
    'graphite.account',
    'graphite.dashboard',
    'graphite.whitelist',
    'graphite.events',
    'tagging',

    'sentry_smtpforwarder',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

SENTRY_KEY = 'Pn9/XwYOZhj/AmWN1tNvqG6D+/NBNHdasZAg+jb1xTD4SA3yZL1I7A=='

# Set this to false to require authentication
SENTRY_PUBLIC = True

# You should configure the absolute URI to Sentry. It will attempt to guess it if you don't
# but proxies may interfere with this.
# SENTRY_URL_PREFIX = 'http://sentry.example.com'  # No trailing slash!

SENTRY_WEB_HOST = '0.0.0.0'
SENTRY_WEB_PORT = 8000

# Mail server configuration

# For more information check Django's documentation:
#  https://docs.djangoproject.com/en/1.3/topics/email/?from=olddocs#e-mail-backends

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'localhost'
EMAIL_HOST_PASSWORD = ''
EMAIL_HOST_USER = ''
EMAIL_PORT = 25
EMAIL_USE_TLS = False

# http://twitter.com/apps/new
# It's important that input a callback URL, even if its useless. We have no idea why, consult Twitter.
TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''

# http://developers.facebook.com/setup/
FACEBOOK_APP_ID = ''
FACEBOOK_API_SECRET = ''

# http://code.google.com/apis/accounts/docs/OAuth2.html#Registering
GOOGLE_OAUTH2_CLIENT_ID = ''
GOOGLE_OAUTH2_CLIENT_SECRET = ''

# https://github.com/settings/applications/new
GITHUB_APP_ID = ''
GITHUB_API_SECRET = ''

# https://trello.com/1/appKey/generate
TRELLO_API_KEY = ''
TRELLO_API_SECRET = ''

USE_JS_CLIENT = True
