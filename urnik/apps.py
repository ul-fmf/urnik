from django.apps import AppConfig
from django.conf import settings

class UrnikConfig(AppConfig):
    name = 'urnik'

    def ready(self):
        if 'django_auth_ldap.backend.LDAPBackend' in settings.AUTHENTICATION_BACKENDS:
            import urnik.signals
