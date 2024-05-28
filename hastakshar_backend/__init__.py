#command needs to be run for the celery:
# celery -A django_celery_project.celery worker --pool=solo  -l info
#beat 
# celery -A django_celery_project  beat -l info
#sendemail
# http://127.0.0.1:8000/sendmail/

#schedule periodic task
# http://127.0.0.1:8000/schedulemail/

#admin admin

from .celery import app as celery_app

__all__ = ('celery_app',)