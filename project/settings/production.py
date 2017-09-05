from .common import *

with open('/srv/urnik/etc/secretkey.txt') as f:
    SECRET_KEY = f.read().strip()

STATIC_ROOT = '/srv/urnik/var/static/'

ALLOWED_HOSTS = ['tyrion.fmf.uni-lj.si']

STATIC_URL = '/nov/static/'

LOGIN_URL = '/nov/accounts/login/'
