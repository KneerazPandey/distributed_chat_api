from celery import shared_task
from core.utils import EmailSender



@shared_task
def forget_password_email_task(email: str, otp: str):
    subject = "Reset Your Forgetten Password"
    text_content = f'Your OTP code is: {otp}'

    EmailSender.send(
        email=email,
        context={
            'otp': otp,
            'email': email,
        },
        subject=subject,
        text_content=text_content,
        html_template_path='accounts/forget_password_otp_email.html',
    )