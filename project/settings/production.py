import ldap
from django_auth_ldap.config import LDAPSearch

from .common import *

with open('/srv/urnik/etc/secretkey.txt') as f:
    SECRET_KEY = f.read().strip()

DEBUG = False

STATIC_ROOT = '/srv/urnik/var/static/'

ALLOWED_HOSTS = ['urnik.fmf.uni-lj.si']

STATIC_URL = '/static/'

LOGIN_URL = '/accounts/login/'

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


AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)

AUTH_LDAP_SERVER_URI = 'ldap://dcv1fmf.fmf.uni-lj.si:3268,ldap://dcv2fmf.fmf.uni-lj.si:3268'
AUTH_LDAP_BIND_DN = 'ldap.pretnar@fmf.uni-lj.si'

with open('/srv/boterdev/etc/ldap_password.txt') as f:
    AUTH_LDAP_BIND_PASSWORD = f.read().strip()

AUTH_LDAP_USER_SEARCH = LDAPSearch('dc=uni-lj,dc=si', ldap.SCOPE_SUBTREE, '(mail=%(user)s)')
AUTH_LDAP_USER_ATTR_MAP = {
    'first_name': 'givenName',
    'last_name': 'sn',
    'email': 'mail'
}
