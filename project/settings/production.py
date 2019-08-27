import ldap
from django_auth_ldap.config import LDAPSearch

from .common import *

with open('/srv/urnik/etc/secretkey.txt') as f:
    SECRET_KEY = f.read().strip()

DEBUG = False

STATIC_ROOT = '/srv/urnik/var/static/'

ALLOWED_HOSTS = ['urnik.fmf.uni-lj.si']

STATIC_URL = '/static/'

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/srv/urnik/var/db.sqlite3',
        'OPTIONS': {
            'timeout': 30,  # seconds
        }
    },
}

with open('/srv/boterdev/etc/ldap_password.txt') as f:
    AUTH_LDAP_BIND_PASSWORD = f.read().strip()
