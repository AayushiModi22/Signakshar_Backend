import logging
from django.core.mail import send_mail
from hastakshar_backend import settings
from celery import shared_task
from send_mail_app.models import ScheduledEmail
from .models import EmailList
from django.utils import timezone
from .models import DocumentTable
logger = logging.getLogger(__name__)

@shared_task
def send_mail_func(scheduled_email_id,scheduled_email_subject,scheduled_email_message):
    try:
        scheduled_email = ScheduledEmail.objects.get(id=scheduled_email_id)
        recipient_email = scheduled_email.recipient_email
        logger.info(f"Sending email to: {recipient_email}")
       
        # Check if the email has already been sent
        if scheduled_email.sent:
            logger.info(f"Email to {recipient_email} has already been sent")
            return

        # Send the email
        mail_subject = scheduled_email_subject
        message = scheduled_email_message
        
        send_mail(
            subject=mail_subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        email_obj = EmailList.objects.get(emails=recipient_email,docId=scheduled_email.doc_id)
        if email_obj.status == 'pending':
            # Update the status of the current email to 'approved'
            email_obj.status = 'sent'
            email_obj.save()
        # Update the scheduled email object to mark it as sent
        scheduled_email.sent = True
        scheduled_email.save()

        logger.info(f"Email sent to {recipient_email} successfully")
    except ScheduledEmail.DoesNotExist:
        logger.error(f"Scheduled email with id {scheduled_email_id} does not exist")
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_email}. Error: {e}")


@shared_task
def delete_expired_documents():
    now = timezone.now()
    expired_documents = DocumentTable.objects.filter(expirationDateTime__lte=now)
    count = expired_documents.count()
    expired_documents.delete()
    return f"{count} expired documents deleted."