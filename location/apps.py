from django.apps import AppConfig


class LocationConfig(AppConfig):
    name = 'location'

    def ready(self):
        import location.signals
