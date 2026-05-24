from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'apps.accounts'

    def ready(self):
        import apps.accounts.handlers.send_user_registered_otp_email_handler
        return super().ready()
