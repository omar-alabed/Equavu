from django.core.mail import send_mail
from django.conf import settings


def send_candidate_email(subject, message, recipient_email):
    """
    Utility to send an email to a candidate.
    """
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [recipient_email],
        fail_silently=False,
    )
