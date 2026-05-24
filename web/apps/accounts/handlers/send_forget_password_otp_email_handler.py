from apps.accounts.events import ForgetPasswordEvent
from core.events import EventRegistry
from apps.accounts.tasks import forget_password_email_task


@EventRegistry.register('accounts.forget.password.event')
def send_forget_password_otp_email_handler(event: ForgetPasswordEvent):
    forget_password_email_task.delay(
        email=event.email,
        otp=event.otp
    )