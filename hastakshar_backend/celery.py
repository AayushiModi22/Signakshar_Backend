from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab
# from send_mail_app.task import delete_expired_documents

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hastakshar_backend.settings')

app = Celery('hastakshar_backend')
app.conf.enable_utc = False
app.conf.update(timezone='Asia/Kolkata')
app.config_from_object(settings, namespace='CELERY')

# celery beat settings
app.conf.beat_schedule = {
    'send-mail-every-day-at-6': {
        'task': 'send_mail_app.task.send_mail_func',
        'schedule': crontab(hour=7, minute=00),
    },
    'send-mail-every-day-at-8': {
        'task': 'send_mail_app.task.send_mail_func',
        'schedule': crontab(hour=15, minute=30),
    },
    'delete-expired-documents': {
        'task': 'send_mail_app.task.delete_expired_documents',
        'schedule': crontab(hour=12, minute=30),  # Run daily at midnight
    },
}