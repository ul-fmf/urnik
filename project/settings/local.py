from .common import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(^hdsfa7b!v0&!pyu2zhd0w($^e&l#qc_q_8dvr)t=ky)fcx87'

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
