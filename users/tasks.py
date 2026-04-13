import random
import string

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from .models import TaskLog


@shared_task
def create_delay_demo_log(note: str = ''):
    random_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    message = f'Delay task generated promo code: {random_code}.'
    if note:
        message += f' Note: {note}'
    log = TaskLog.objects.create(task_type='delay', message=message)
    return {'task_log_id': log.id, 'promo_code': random_code}


@shared_task
def create_crontab_heartbeat_log():
    log = TaskLog.objects.create(
        task_type='crontab',
        message='Scheduled heartbeat log was created by Celery Beat.',
    )
    return {'task_log_id': log.id}


@shared_task
def send_demo_email_task(recipient_email: str, subject: str = '', body: str = ''):
    subject = subject or 'Celery SMTP demo'
    body = body or 'This email was sent by Celery using SMTP settings.'
    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [recipient_email],
        fail_silently=False,
    )
    log = TaskLog.objects.create(
        task_type='smtp',
        recipient_email=recipient_email,
        message=f'SMTP email sent. Subject: {subject}',
    )
    return {'task_log_id': log.id, 'recipient_email': recipient_email}
