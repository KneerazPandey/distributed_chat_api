from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string



@shared_task
def send_user_registered_email_task(email: str, otp: str):
    subject = "Verify Your Email"
    html_content = render_to_string(
        'accounts/registered_otp_email.html', 
        context={
            'otp': otp,
            'email': email,
        }
    )
    text_content = f'Your OTP code is: {otp}'

    message = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        to=[email]
    )

    message.attach_alternative(html_content, 'text/html')

    message.send()