from django.apps import AppConfig


class UrnikConfig(AppConfig):
    name = 'urnik'

    def ready(self):
        import urnik.signals
