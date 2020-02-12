from django.apps import AppConfig


class BankConfig(AppConfig):
    name = 'bank'

    def ready(self):
        import bank.signals