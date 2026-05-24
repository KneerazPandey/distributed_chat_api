from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


class EmailSender:
    @staticmethod
    def send(email: str, subject: str, text_content: str, context: dict, html_template_path: str):
        subject = subject
        html_content = render_to_string(
            html_template_path, 
            context=context
        )
        text_content = text_content

        message = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            to=[email]
        )

        message.attach_alternative(html_content, 'text/html')

        message.send()