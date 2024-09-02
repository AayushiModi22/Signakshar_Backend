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
    # 'send-mail-every-day-at-6': {
    #     'task': 'send_mail_app.task.send_mail_func',
    #     'schedule': crontab(hour=7, minute=00),
    # },
    # 'send-mail-every-day-at-8': {
    #     'task': 'send_mail_app.task.send_mail_func',
    #     'schedule': crontab(hour=15, minute=30),
    # },
    'delete-expired-documents': {
        'task': 'send_mail_app.task.delete_expired_documents',
        'schedule': crontab(hour=00, minute=00),  # Run daily at noon
    },
}

# rajvi's code
# celery.py

# from __future__ import absolute_import, unicode_literals
# import os
# from celery import Celery
# from django.conf import settings
# from celery.schedules import crontab

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hastakshar_backend.settings')

# app = Celery('hastakshar_backend')
# app.conf.enable_utc = False
# app.conf.update(timezone='Asia/Kolkata')
# app.config_from_object(settings, namespace='CELERY')

# # Celery beat settings
# app.conf.beat_schedule = {
#     'delete-expired-documents': {
#         'task': 'send_mail_app.task.delete_expired_documents',
#         'schedule': crontab(hour=15, minute=0),  # Runs daily at 15:00 IST
#     },
#     'delete-file-from-s3': {
#         'task': 'send_mail_app.tasks.delete_file_from_s3',
#         'schedule': crontab(hour=17, minute=55),  # Runs daily at 15:00 IST
#         'args': ('sign-3-rajvigajjar2003', 'Profile_1724672216638.pdf')  # Example arguments
#     },
# }

# app.autodiscover_tasks()
