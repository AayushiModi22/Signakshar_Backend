# currently working for the no of days... 
from django.db import models
from django.utils import timezone
from mainapp.models import DocumentTable

class ScheduledEmail(models.Model):
    recipient_email = models.EmailField()
    scheduled_time = models.DateTimeField()
    expiration_days = models.IntegerField(default=0)
    reminder_date_pm = models.DateTimeField(null=True, blank=True)  # Reminder for 4:00:00 PM
    reminder_date_am = models.DateTimeField(null=True, blank=True)  # Reminder for 10:00:00 AM
    sent = models.BooleanField(default=False)
    doc_id = models.ForeignKey(DocumentTable, on_delete=models.CASCADE, related_name='scheduled_emails')

    def __str__(self):
        return f"Email to {self.recipient_email} scheduled at {self.scheduled_time}"

    def calculate_expiration_days(self):
        """
        Calculate the expiration days based on the scheduled time and current date.
        """
        current_time = timezone.now()
        difference = self.scheduled_time.date() - current_time.date()  # Calculate difference in days only
        self.expiration_days = difference.days if difference.days > 0 else 0
        self.save()

class EmailList(models.Model):
    PENDING = 'pending'
    SENT = 'sent'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (SENT, 'Sent'),
    ]
    
    emails = models.EmailField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    docId = models.ForeignKey(DocumentTable, on_delete=models.CASCADE, related_name='email_lists')
    def __str__(self):
        return f"Email List - {self.emails}"
    
