from .common import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(^hdsfa7b!v0&!pyu2zhd0w($^e&l#qc_q_8dvr)t=ky)fcx87'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'OPTIONS': {
            'timeout': 30,  # seconds
        }
    }
}

MIDDLEWARE.insert(0, 'silk.middleware.SilkyMiddleware')

INSTALLED_APPS += [
    'silk',
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django_auth_ldap': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}


import ldap
from django_auth_ldap.config import LDAPSearch


with open('ldap_password.txt') as f:
    AUTH_LDAP_BIND_PASSWORD = f.read().strip()

AUTH_LDAP_SERVER_URI = 'ldap://dcv1fmf.fmf.uni-lj.si:3268,ldap://dcv2fmf.fmf.uni-lj.si:3268'
AUTH_LDAP_BIND_DN = 'ldap.pretnar@fmf.uni-lj.si'

AUTH_LDAP_USER_SEARCH = LDAPSearch('dc=uni-lj,dc=si', ldap.SCOPE_SUBTREE, '(mail=%(user)s)')
AUTH_LDAP_USER_ATTR_MAP = {
    'first_name': 'givenName',
    'last_name': 'sn',
    'email': 'mail'
}
