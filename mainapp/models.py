from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import timedelta


class User(AbstractUser):
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    username = None
    full_name = models.CharField(max_length=300, blank=True, null=True)
    initial = models.CharField(max_length=10, blank=True, null=True)
    # stamp_img_name = models.CharField(max_length=255, blank=True, null=True)
    stamp_img_name = models.TextField(blank=True, null=True)
    stamp_enc_key = models.CharField(max_length=255, blank=True, null=True)
    s3Key = models.CharField(max_length=255, blank=True, null=True)
    signIn_with_google=models.CharField(max_length=10, blank=True, null=True,default='N')
    profile_pic = models.TextField(blank=True, null=True)

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=[]

class otpUser(models.Model):
    email = models.EmailField(max_length=100, unique=True)
    otp = models.IntegerField(max_length=6)
    status = models.CharField(max_length=1,default='N')
    entry_date = models.DateTimeField(auto_now_add=True)

class Signature(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    draw_img_name = models.TextField(blank=True, null=True)
    draw_enc_key = models.CharField(max_length=255, blank=True, null=True)
    img_name = models.TextField(blank=True, null=True)
    img_enc_key = models.CharField(max_length=255, blank=True, null=True)

class Initials(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    draw_img_name = models.TextField(blank=True, null=True)
    draw_enc_key = models.CharField(max_length=255, blank=True, null=True)
    img_name = models.TextField(blank=True, null=True)
    img_enc_key = models.CharField(max_length=255, blank=True, null=True)

class RecipientRole(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=100, unique=True)
    
class DocumentTable(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    pdfName = models.CharField(max_length=100)
    creationDateTime = models.DateTimeField(default=timezone.now)
    size = models.IntegerField()
    s3Key = models.CharField(max_length=100)
    creator_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='positions_sent',default=1)
    status = models.CharField(max_length=100)
    email_title = models.CharField(max_length=100)
    email_msg = models.CharField(max_length=500)  
    req_type = models.CharField(max_length=1,default='N')  
    Schedule_type = models.CharField(max_length=1,default='N')  
    last_modified_date_time = models.DateTimeField(default=timezone.now)
    last_modified_by = models.ForeignKey(User, default=1,on_delete=models.CASCADE, related_name='documents_last_modified')
    expirationDateTime = models.DateTimeField(default=timezone.now()+timedelta(days=7))
    reminderDays = models.IntegerField()

class DocumentRecipientDetail(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    roleId = models.ForeignKey(RecipientRole, on_delete=models.CASCADE,default=1)
    docId = models.ForeignKey('DocumentTable', on_delete=models.CASCADE)   

    
class RecipientPositionData(models.Model):
    signer_status_options = (
        ('Signed', 'Signed'),
        ('Unsigned', 'Unsigned'),
    )    
    reviewer_status_options = (
        ('Approved', 'Approved'),
        ('Declined', 'Declined'),
    )
    id = models.AutoField(primary_key=True)
    fieldName = models.CharField(max_length=100)
    color = models.CharField(max_length=50)
    # name = models.CharField(max_length=100)
    boxId = models.CharField(max_length=100)
    pageNum = models.IntegerField()
    x = models.FloatField()  
    y = models.FloatField()  
    width = models.FloatField()
    height = models.FloatField()
    docId = models.ForeignKey('DocumentTable', on_delete=models.CASCADE)
    # roleId = models.ForeignKey(RecipientRole, on_delete=models.CASCADE,default=1)
    signer_status = models.CharField(max_length=100, choices=signer_status_options, unique=False)
    reviewer_status = models.CharField(max_length=100, choices=reviewer_status_options, unique=False)
    docRecipientdetails_id = models.ForeignKey(DocumentRecipientDetail, on_delete=models.CASCADE,default=1)
    # sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='positions_sent',default=1)
    # receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='positions_received',default=2)


# class BulkPdfDocumentTable(models.Model):
#     id = models.AutoField(primary_key=True)
#     name = models.CharField(max_length=100)
#     # pdfName = models.CharField(max_length=100)
#     # size = models.IntegerField()
#     selectedPdfs = models.JSONField()
#     creationDateTime = models.DateTimeField(default=timezone.now)
#     s3Key = models.CharField(max_length=100)
#     creator_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='positions_sent_bulkpdf',default=1)
#     status = models.CharField(max_length=100)
    
# class BulkPdfPositionData(models.Model):
#     signer_status_options = (
#         ('Signed', 'Signed'),
#         ('Unsigned', 'Unsigned'),
#     )    
#     reviewer_status_options = (
#         ('Approved', 'Approved'),
#         ('Declined', 'Declined'),
#     )
#     id = models.AutoField(primary_key=True)
#     fieldName = models.CharField(max_length=100)
#     color = models.CharField(max_length=50)
#     name = models.CharField(max_length=100)
#     email = models.EmailField()
#     # fileName = models.CharField(max_length=100)  
#     boxId = models.CharField(max_length=100)
#     pageNum = models.IntegerField()
#     x = models.FloatField()  
#     y = models.FloatField()  
#     width = models.FloatField()
#     height = models.FloatField()
#     docId = models.ForeignKey('BulkPdfDocumentTable', on_delete=models.CASCADE)
#     roleId = models.ForeignKey(RecipientRole, on_delete=models.CASCADE,default=1)
#     signer_status = models.CharField(max_length=100, choices=signer_status_options, unique=True)
#     reviewer_status = models.CharField(max_length=100, choices=reviewer_status_options, unique=True)

# sakshi changes

class BulkPdfDocumentTable(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    # pdfName = models.CharField(max_length=100)
    # size = models.IntegerField()
    selectedPdfs = models.JSONField()
    creationDateTime = models.DateTimeField(default=timezone.now)
    s3Key = models.CharField(max_length=100)
    creator_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='positions_sent_bulkpdf',default=1)
    status = models.CharField(max_length=100)
    email_title = models.CharField(max_length=100,default="Hello")
    email_msg = models.CharField(max_length=500,default="Hello")  
    req_type = models.CharField(max_length=1,default='N')  
    Schedule_type = models.CharField(max_length=1,default='N')  
    last_modified_date_time = models.DateTimeField(default=timezone.now)
    last_modified_by = models.ForeignKey(User, default=1,on_delete=models.CASCADE, related_name='bulk_documents_last_modified')
    expirationDateTime = models.DateTimeField(default=timezone.now()+timedelta(days=7))
    reminderDays = models.IntegerField(default=15)
    

class BulkPdfRecipientDetail(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    docId = models.ForeignKey('BulkPdfDocumentTable', on_delete=models.CASCADE)
    roleId = models.ForeignKey(RecipientRole, on_delete=models.CASCADE,default=1)
    def _str_(self):
        return self.name

class BulkPdfPositionData(models.Model):
    signer_status_options = (
        ('Signed', 'Signed'),
        ('Unsigned', 'Unsigned'),
    )    
    reviewer_status_options = (
        ('Approved', 'Approved'),
        ('Declined', 'Declined'),
    )
    id = models.AutoField(primary_key=True)
    fieldName = models.CharField(max_length=100)
    color = models.CharField(max_length=50)
    #name = models.CharField(max_length=100)
    #email = models.EmailField()
    # fileName = models.CharField(max_length=100)  
    boxId = models.CharField(max_length=100)
    pageNum = models.IntegerField()
    x = models.FloatField()  
    y = models.FloatField()  
    width = models.FloatField()
    height = models.FloatField()
    docId = models.ForeignKey('BulkPdfDocumentTable', on_delete=models.CASCADE)
    #roleId = models.ForeignKey(RecipientRole, on_delete=models.CASCADE,default=1)
    signer_status = models.CharField(max_length=100, choices=signer_status_options, unique=True)
    reviewer_status = models.CharField(max_length=100, choices=reviewer_status_options, unique=True)
    bulkpdf_recipient_detail_id = models.ForeignKey('BulkPdfRecipientDetail', on_delete=models.CASCADE,default=1)
        
# ///////


class Template(models.Model):
    template_id = models.AutoField(primary_key=True) 
    templateName = models.CharField(max_length=255)  
    createTempfile = models.CharField(max_length=255)
    templateNumPages = models.IntegerField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def str(self):
        return self.templateName

class TemplateRecipient(models.Model):
    template = models.ForeignKey(Template, related_name='template', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(RecipientRole, on_delete=models.CASCADE)
    
class TemplateDraggedData(models.Model):
    templateRec = models.ForeignKey(TemplateRecipient,related_name='template_recipient',on_delete=models.CASCADE)
    template = models.ForeignKey(Template, related_name='dragged_data', on_delete=models.CASCADE)
    fieldName = models.CharField(max_length=255, null=True)  # Allow null
    color = models.CharField(max_length=50,null=True) #allow null
    # name = models.CharField(max_length=255)
    recBoxid = models.CharField(max_length=255, null=True)  # Allow null
    pageNum = models.IntegerField(null=True)  # Allow null
    x = models.FloatField(null=True)  # Allow null
    y = models.FloatField(null=True)  # Allow null
    width = models.FloatField(null=True)  # Allow null
    height = models.FloatField(null=True)  # Allow null
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(RecipientRole, on_delete=models.CASCADE)

    def str(self):
        return self.name
    
class UseTemplateRecipient(models.Model):
    signer_status_options = (
        ('Signed', 'Signed'),
        ('Unsigned', 'Unsigned'),
    )    
    reviewer_status_options = (
        ('Approved', 'Approved'),
        ('Declined', 'Declined'),
        ('InProgress','InProgress')
    )
    RecipientName = models.CharField(max_length=255)
    RecipientEmail = models.EmailField()
    templateRec = models.ForeignKey(TemplateRecipient,related_name='temp_recipient',on_delete=models.CASCADE)
    # dragged_data = models.ForeignKey('TemplateDraggedData', related_name='recipients', on_delete=models.CASCADE)
    template = models.ForeignKey('Template', related_name='recipients', on_delete=models.CASCADE)
    dummy_name = models.CharField(max_length=255)
    userSelectfile = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(RecipientRole, on_delete=models.CASCADE) 
    docid=models.ForeignKey(DocumentTable,on_delete=models.CASCADE)
    signer_status = models.CharField(max_length=100, choices=signer_status_options)
    reviewer_status = models.CharField(max_length=100, choices=reviewer_status_options)

    def str(self):
        return self.RecipientName