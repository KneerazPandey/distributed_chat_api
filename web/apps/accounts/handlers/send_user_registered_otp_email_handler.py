from apps.accounts.events import UserRegisteredEvent
from core.events import EventRegistry
from apps.accounts.tasks import send_user_registered_email_task


@EventRegistry.register('accounts.user.registered.event')
def send_user_registered_otp_email_handler(event: UserRegisteredEvent):
    send_user_registered_email_task.delay(
        email=event.email,
        otp=event.otp
    )