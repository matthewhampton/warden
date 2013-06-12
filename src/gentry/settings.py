"""
gentry.settings
---------------
"""
from sentry.conf.server import MIDDLEWARE_CLASSES as SENTRY_MIDDLEWARE_CLASSES 
from graphite.settings import  MIDDLEWARE_CLASSES as GRAPHITE_MIDDLEWARE_CLASSES
from sentry.conf.server import INSTALLED_APPS as SENTRY_INSTALLED_APPS
from graphite.settings import INSTALLED_APPS as GRAPHITE_INSTALLED_APPS
from graphite.settings import *
from sentry.conf.server import *
import logging
import os

# A tuple of tuples containing the name and email of people to email when an error occurs.
# ADMINS = (('John', 'john@smith.com'))
ADMINS = ()

def get_databases(warden_home):
    # Change this to the path where the database file will be stored.
    _data_root = os.path.abspath(os.path.join(warden_home, 'gentry'))

    return {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',     # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': os.path.join(_data_root, 'gentry.db'),   # Or path to database file if using sqlite3.
            'USER': '',                                 # Not used with sqlite3.
            'PASSWORD': '',                             # Not used with sqlite3.
            'HOST': '',                                 # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '',                                 # Set to empty string for default. Not used with sqlite3.
        }
    }

# Make this unique, and don't share it with anybody.
#SENTRY_KEY = e.g. 'Pn9/XwYOZhj/AmWN1tNvqG6D+/NBNHdasZAg+jb1xTD4SA3yZL1I7A=='

# Set this to false to require authentication
SENTRY_PUBLIC = True

# You should configure the absolute URI to Sentry. It will attempt to guess it if you don't
# but proxies may interfere with this.
# SENTRY_URL_PREFIX = 'http://sentry.example.com'  # No trailing slash!

SENTRY_WEB_HOST = '0.0.0.0'
SENTRY_WEB_PORT = 9000

# Sentry mailer level
SENTRY_MAIL_LEVEL = logging.ERROR


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

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!! DONT TOUCH ANY SETTINGS AFTER THIS !!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Combine the middleware classes. We don't use sets here because the order matters and sets just don't respect that.
# There is conceivably a problem if the GRAPHITE_MIDDLEWARE_CLASSES that overlap with the
# SENTRY_MIDDLEWARE_CLASSES appear in a different order in the SENTRY_MIDDLEWARE_CLASSES list, 
# but that is not the case with the current versions, so we are alright.
MIDDLEWARE_CLASSES = list(SENTRY_MIDDLEWARE_CLASSES) + [cls for cls in GRAPHITE_MIDDLEWARE_CLASSES if cls not in SENTRY_MIDDLEWARE_CLASSES]

INSTALLED_APPS = ('gentry', 'sentry_jsonmailprocessor') + tuple(set(SENTRY_INSTALLED_APPS).union(set(GRAPHITE_INSTALLED_APPS)))

ROOT_URLCONF = 'gentry.urls'

WSGI_APPLICATION = 'gentry.wsgi.application'

CONF_ROOT = os.path.dirname(__file__)

DEBUG = True

MEDIA_URL = ''
