import logging
from django.core.mail import send_mail
from hastakshar_backend import settings
from celery import shared_task
from send_mail_app.models import ScheduledEmail
from .models import EmailList
from django.utils import timezone
from .models import DocumentTable
from django.core.mail import EmailMultiAlternatives
import boto3
from django.conf import settings
from mainapp.models import User

logger = logging.getLogger(__name__)

# @shared_task
# def send_mail_func(scheduled_email_id, scheduled_email_subject, text_content, html_content):
#     try:
#         scheduled_email = ScheduledEmail.objects.get(id=scheduled_email_id)
#         recipient_email = scheduled_email.recipient_email
#         logger.info(f"Sending email to: {recipient_email}")
       
#         # Check if the email has already been sent
#         if scheduled_email.sent:
#             logger.info(f"Email to {recipient_email} has already been sent")
#             return

#         # Send the email with HTML content
#         email = EmailMultiAlternatives(
#             subject=scheduled_email_subject,
#             body=text_content,
#             from_email=settings.EMAIL_HOST_USER,
#             to=[recipient_email]
#         )
#         email.attach_alternative(html_content, "text/html")
#         email.send()

#         email_obj = EmailList.objects.get(emails=recipient_email, docId=scheduled_email.doc_id)
#         if email_obj.status == 'pending':
#             email_obj.status = 'sent'
#             email_obj.save()

#         scheduled_email.sent = True
#         scheduled_email.save()

#         logger.info(f"Email sent to {recipient_email} successfully")
#     except ScheduledEmail.DoesNotExist:
#         logger.error(f"Scheduled email with id {scheduled_email_id} does not exist")
#     except Exception as e:
#         logger.error(f"Failed to send email to {recipient_email}. Error: {e}")

@shared_task
def send_mail_func(scheduled_email_id, scheduled_email_subject, text_content, html_content):
    # print("inside_send_mail_func")
    print("=========text_content=======send_mail_app",text_content)
    print("=========text_content=======send_mail_app",scheduled_email_id, scheduled_email_subject, text_content, html_content)
    try:
        scheduled_email = ScheduledEmail.objects.get(id=scheduled_email_id)
        recipient_email = scheduled_email.recipient_email
        logger.info(f"Sending email to: {recipient_email}")
        
        # Check if the email has already been sent
        if scheduled_email.sent:
            logger.info(f"Email to {recipient_email} has already been sent")
            return

        # Send the email with HTML content
        email = EmailMultiAlternatives(
            subject=scheduled_email_subject,
            body=text_content,
            from_email=settings.EMAIL_HOST_USER,
            to=[recipient_email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

        email_obj = EmailList.objects.get(emails=recipient_email, docId=scheduled_email.doc_id)
        if email_obj.status == 'pending':
            email_obj.status = 'sent'
            email_obj.save()

        scheduled_email.sent = True
        scheduled_email.save()

        logger.info(f"Email sent to {recipient_email} successfully")
    except ScheduledEmail.DoesNotExist:
        logger.error(f"Scheduled email with id {scheduled_email_id} does not exist")
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_email}. Error: {e}")
       
# @shared_task
# def delete_expired_documents():
#     now = timezone.now()
#     expired_documents = DocumentTable.objects.filter(expirationDateTime__lte=now)
#     count = expired_documents.count()
#     expired_documents.delete()
#     return f"{count} expired documents deleted."

@shared_task
def delete_expired_documents():
    now = timezone.now()
    expired_documents = DocumentTable.objects.filter(expirationDateTime__lte=now)
    
    if not expired_documents.exists():
        return "No expired documents to delete."

    # Initialize S3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )

    count = 0
    for document in expired_documents:
        try:
            # Retrieve the user's email to determine the bucket name
            user = User.objects.get(id=document.creator_id.id)
            bucket_name = f"sign-{user.id}-{user.email.split('@')[0]}"
            file_name = document.name+".pdf"
            
            # Delete the document from S3
            s3_client.delete_object(Bucket=bucket_name, Key=file_name)
            
            # Delete the document from your database
            document.delete()
            
            count += 1
            print(f"Deleted {file_name} from bucket {bucket_name} and removed from database.")
        except User.DoesNotExist:
            print(f"User with id {document.creator_id} does not exist.")
        except Exception as e:
            print(f"Error deleting document {document.name}: {e}")

    return f"{count} expired documents deleted."
