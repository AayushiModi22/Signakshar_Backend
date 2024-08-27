from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
import json
from django.http import JsonResponse
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from django.views.decorators.http import require_POST
from decouple import config

from mainapp.myviews.user_views import JWTAuthentication
from mainapp.models import User,RecipientRole,DocumentTable,DocumentRecipientDetail,RecipientPositionData,Template
from mainapp.serializers import DocumentTableSerializer,DocumentRecipientSerializer,DocumentPositionSerializer,EmailListSerializer

from django.shortcuts import render
from mainapp.task import tasc_func
from send_mail_app.task import send_mail_func
from django_celery_beat.models import PeriodicTask,CrontabSchedule
from django.utils import timezone
from django.utils.text import slugify
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime,timedelta
from send_mail_app.models import ScheduledEmail
from django.http import HttpResponse
from send_mail_app.models import EmailList
from django.core.mail import send_mail
from django.conf import settings
import logging
import time
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
# from django.shortcuts import get_object_or_404
from datetime import time
from django.shortcuts import redirect
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from ..decorators.logging import log_api_request 


logger = logging.getLogger(__name__)

class DocumentTableViewset(viewsets.ModelViewSet):
    queryset=DocumentTable.objects.all()
    serializer_class=DocumentTableSerializer
 
    def get_queryset(self):
        user = self.request.user
        queryset = DocumentTable.objects.filter(creator_id=user)
 
        return queryset

    def create(self, request, *args, **kwargs):
        doc_name = request.data.get('name')
        userid = request.data.get('creator_id')
 
        existing_template = DocumentTable.objects.filter(
            name=doc_name, creator_id=userid
        ).exists()
 
        if existing_template:
            return Response(
                {"error": "Document with the same name already exists for this user."}
                # status=status.HTTP_400_BAD_REQUEST
            )
 
        return super().create(request, *args, **kwargs)
 
    def get_permissions(self):
        if self.request.method == 'POST':
            # For POST requests, return an empty list to skip permission checks
            return []
        else:
            # For other request methods (GET, PUT, PATCH, DELETE), apply IsAuthenticated permission
            return [IsAuthenticated()]
 
    def get_authenticators(self):
        if self.request.method == 'POST':
            # For POST requests, return an empty list to skip authentication
            return []
        else:
            # For other request methods (GET, PUT, PATCH, DELETE), apply JWTAuthentication
            return [JWTAuthentication()]
       
class DocumentByDocId(APIView):
    # authentication_classes = [JWTAuthentication]  
    # permission_classes = [IsAuthenticated]
    def get(self, request, doc_id):
        try:
            print("doc_views get DocumentByDocId")
            # Retrieve Template object based on the provided template_id
            doc_data = DocumentTable.objects.get(id=doc_id)
            serializer = DocumentTableSerializer(doc_data)
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        except Template.DoesNotExist:
            return JsonResponse({"error": "Document Data not found for the given document_id"}, status=status.HTTP_404_NOT_FOUND)
     
from rest_framework.parsers import JSONParser
# save document withouth template
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

# #original
class EmailListAPIView(APIView):
    def get(self, request, docId, recEmail):
        email_list = EmailList.objects.filter(docId=docId, emails=recEmail)
        serializer = EmailListSerializer(email_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, docId, recEmail):
        try:
            data = JSONParser().parse(request)

            if 'doc_id' not in data:
                return JsonResponse({"error": "doc_id is required"}, status=400)

            doc_id = data["doc_id"]
            email_id = recEmail
            status_update = data.get("status")

            reciever_panel_endpoint = config('RECIEVER_PANEL_ENDPOINT')


            doc = DocumentTable.objects.get(pk=doc_id)
            print("doc datetime : ",doc.expirationDateTime," doc.reminderDays : ",doc.reminderDays)
            recipient_detail = DocumentRecipientDetail.objects.filter(email=email_id, docId=doc_id).first()
            print("recipient_detail : ",recipient_detail)
            if not recipient_detail:
                return JsonResponse({"error": "Recipient data not found..!!"}, status=404)

            text_content = ""
            html_content = ""

            # Sequential signing
            if doc.req_type == "S":
                email_obj = EmailList.objects.filter(docId=doc_id, emails=email_id).first()
                print("email_obj 1 : ",email_obj)
                print("email_obj 2 : ",email_obj.status)
                if email_obj and email_obj.status == 'sent':
                    email_obj.status = status_update if status_update else 'approved'
                    email_obj.save()

                    next_pending_email = EmailList.objects.filter(status='pending', docId=doc_id).first()
                    print("email_obj 5 : ",next_pending_email)
                    print("email_obj 6 : ",next_pending_email.emails)

                    if next_pending_email:
                        print("email_obj 7 : ",next_pending_email)
                        print("email_obj 8 : ",next_pending_email.emails)
                        recipients = DocumentRecipientDetail.objects.filter(docId=doc_id, email=next_pending_email.emails).first()
                        print("email_obj 9 : ",recipients)
                        print("email_obj 10 : ",recipients.email)
                        if recipients:
                            if recipients.roleId.role_id == 1:  # Signer
                                url = f"{reciever_panel_endpoint}#/recieverPanel?docType=doc&type=signer&did={doc_id}&rid={recipients.id}"
                                message = doc.email_msg + f"\n\nThank you for choosing Signakshar. Click on the following link to sign the document: {url} \nIgnore this reminder if you have already signed the document."
                            elif recipients.roleId.role_id == 2:  # Viewer
                                url = f"{reciever_panel_endpoint}#/recieverPanel?docType=doc&type=viewer&did={doc_id}&rid={recipients.id}"
                                message = doc.email_msg + f"\n\nThank you for choosing Signakshar. Click on the following link to view the document: {url} \nIgnore this reminder if you have already viewed the document."

                        
                            html_content = render_to_string('otp-template/document-signing.html', {
                                'reciever_link': url,
                                'username': next_pending_email.emails.split('@')[0],
                                'message': doc.email_msg,
                                'recRole': recipients.roleId.role_id
                            })
                            text_content = strip_tags(html_content)

                            schedule_sequence_email({
                                "email": next_pending_email.emails,
                                "reminderDays": doc.reminderDays,
                                "scheduledDate": doc.expirationDateTime,
                                "doc_id": doc_id,
                                "title": doc.email_title,
                                "message": message,
                                "text_content": text_content,
                                "html_content": html_content
                            })
                            send_mail_to_sequence_recipient(next_pending_email.emails, doc.email_title, text_content, html_content, doc_id)

                            return JsonResponse({"success": "Email sent to next recipient"}, safe=False, status=200)
                    else:
                        doc.status = "Completed"
                        doc.save()
                        return JsonResponse({"success": "Document completed successfully"}, status=200)
                else:
                    return JsonResponse({"error": "Email has already been sent or not found..!!"}, status=400)

            # Notify all recipients simultaneously
            elif doc.req_type == "N":
                email_obj = EmailList.objects.filter(docId=doc_id, emails=email_id).first()
                print("email_obj 3 : ",email_obj)
                print("email_obj 4 : ",email_obj.status)
                if email_obj and email_obj.status == 'sent':
                    email_obj.status = status_update if status_update else 'approved'
                    email_obj.save()

                email_obj_list = EmailList.objects.filter(docId=doc_id)
                all_approved = all(email.status == 'approved' for email in email_obj_list)

                if all_approved:
                    doc.status = "Completed"
                    doc.save()
                    return JsonResponse({"success": "Document completed successfully"}, status=200)
                else:
                    return JsonResponse({"success": "Recipient approved but awaiting others"}, status=200)

            # Handle concurrent recipients
            elif doc.req_type == "C":
                email_obj = EmailList.objects.filter(docId=doc_id, emails=email_id).first()
                if email_obj and email_obj.status == 'sent':
                    email_obj.status = status_update if status_update else 'approved'
                    email_obj.save()
                    next_pending_emails = EmailList.objects.filter(status='pending', docId=doc_id)

                    if next_pending_emails.exists():
                        for pending_email in next_pending_emails:
                            recipients = DocumentRecipientDetail.objects.filter(docId=doc_id, email=pending_email.emails).first()
                            if recipients:
                                if recipients.roleId.role_id == 1:
                                    url = f"{reciever_panel_endpoint}#/recieverPanel?docType=doc&type=signer&did={doc_id}&rid={recipients.id}"
                                    message = doc.email_msg + f"\n\nThank you for choosing Signakshar. Click on the following link to sign the document: {url} \nIgnore this reminder if you have already signed the document."
                                elif recipients.roleId.role_id == 2:
                                    url = f"{reciever_panel_endpoint}#/recieverPanel?docType=doc&type=viewer&did={doc_id}&rid={recipients.id}"
                                    message = doc.email_msg + f"\n\nThank you for choosing Signakshar. Click on the following link to view the document: {url} \nIgnore this reminder if you have already viewed the document."

                                html_content = render_to_string('otp-template/document-signing.html', {
                                    'reciever_link': url,
                                    'username': pending_email.emails.split('@')[0],
                                    'message': doc.email_msg,
                                    'recRole': recipients.roleId.role_id
                                })
                                text_content = strip_tags(html_content)

                                schedule_sequence_email({
                                    "email": pending_email.emails,
                                    "reminderDays": doc.reminderDays,
                                    "scheduledDate": doc.expirationDateTime,
                                    "doc_id": doc_id,
                                    "title": doc.email_title,
                                    "message": message,
                                    "text_content": text_content,
                                    "html_content": html_content
                                })
                                send_mail_to_sequence_recipient(pending_email.emails, doc.email_title, text_content, html_content, doc_id)


                    email_obj_list = EmailList.objects.filter(docId=doc_id)
                    all_approved = all(email.status == 'approved' for email in email_obj_list)

                    if all_approved:
                        doc.status = "Completed"
                        doc.save()
                        return JsonResponse({"success": "Document completed successfully"}, status=200)
                    else:
                        return JsonResponse({"success": "Emails sent to next recipients."}, status=200)
                else:
                    return JsonResponse({"error": "Email has already been sent or not found..!!"}, status=400)

        except DocumentTable.DoesNotExist:
            return JsonResponse({"error": "Document not found"}, status=404)
        except EmailList.DoesNotExist:
            return JsonResponse({"error": "Email not found"}, status=404)
        except Exception as e:
            print("Exception occurred:", str(e))
            return JsonResponse({"error": str(e)}, status=400)

       
class DocumentRecipientDetailAPIView(APIView):
    def get(self, request, docId, recEmail):
        print("doc_views DocumentRecipientDetailAPIView get")
        recipient_details = DocumentRecipientDetail.objects.filter(docId=docId, email=recEmail)
        serializer = DocumentRecipientSerializer(recipient_details, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class FetchRecipientFullDetails(APIView):
    def get(self, request, recipient_id):
        try:
            print("doc_views FetchRecipientFullDetails get")
            recipient_detail = DocumentRecipientDetail.objects.get(pk=recipient_id)
            serializer = DocumentRecipientSerializer(recipient_detail)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except DocumentRecipientDetail.DoesNotExist:
            return Response({"error": "Recipient not found"}, status=status.HTTP_404_NOT_FOUND)
 
# Save the document record along with recipient detail
# @csrf_exempt
# @log_api_request
# def save_doc(request):
#     try:
#         print("doc_views save_doc")
#         if request.method == 'POST':
#             data = JSONParser().parse(request)
#             doc_name = data['name']
#             userid = data['creator_id']
#             print("data:",data)
#             user = User.objects.get(pk=userid)

#             existing_template = DocumentTable.objects.filter(
#                 name=doc_name, creator_id=user
#             ).exists()

#             if existing_template:
#                 return JsonResponse(
#                     {"error": "Document with the same name already exists for this user."},
#                     status=400
#                 )

#             # Create the document
#             document = DocumentTable.objects.create(
#                 name=data['name'],
#                 pdfName=data['pdfName'],
#                 size=data['size'],
#                 s3Key=data['s3Key'],
#                 status=data['status'],
#                 email_title=data['email_title'],
#                 email_msg=data['email_message'],
#                 creator_id=user,
#                 req_type=data['emailAction'],
#                 expirationDateTime=data['scheduledDate'],
#                 reminderDays=data['reminderDays'],
#             )
#             document_id = document.id
#             recipients = [
#                 DocumentRecipientDetail(
#                     name=recipient_data['RecipientName'],
#                     email=recipient_data['RecipientEmail'],
#                     roleId=RecipientRole.objects.filter(
#                         role_name = recipient_data["role"]
#                     ).first(),
#                     docId= document
#                 )
#                 for recipient_data in data['receipientData']
#             ]
#             DocumentRecipientDetail.objects.bulk_create(recipients)
#             return JsonResponse({"doc_id":document.id,"message": "Document and recipients created successfully."})
#         else:
#             return JsonResponse({"error": "Invalid request method"}, status=405)
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=400)

# /// rajvi new api for deleting rec if docid exists and then further document entry gets inserted
@csrf_exempt
@log_api_request
def save_doc(request):
    try:
        print("doc_views save_doc")
        if request.method == 'POST':
            data = JSONParser().parse(request)
            doc_name = data['name']
            userid = data['creator_id']
            doc_id = data.get('doc_id')  # Fetch doc_id if it exists
            user = User.objects.get(pk=userid)

            # If doc_id exists, update the existing document
            if doc_id:
                try:
                    document = DocumentTable.objects.get(pk=doc_id)
                    
                    # Delete existing recipients
                    DocumentRecipientDetail.objects.filter(docId=document).delete()

                    # Update the document fields
                    document.name = doc_name
                    document.pdfName = data['pdfName']
                    document.size = data['size']
                    document.s3Key = data['s3Key']
                    document.status = data['status']
                    document.email_title = data['email_title']
                    document.email_msg = data['email_message']
                    document.req_type = data['emailAction']
                    document.expirationDateTime = data['scheduledDate']
                    document.reminderDays = data['reminderDays']
                    document.save()
                except DocumentTable.DoesNotExist:
                    return JsonResponse({"error": "Document not found."}, status=404)

            else:
                # If doc_id does not exist, check for existing template
                existing_template = DocumentTable.objects.filter(
                    name=doc_name, creator_id=user
                ).exists()

                if existing_template:
                    return JsonResponse(
                        {"error": "Document with the same name already exists for this user."},
                        status=400
                    )

                # Create the document
                document = DocumentTable.objects.create(
                    name=data['name'],
                    pdfName=data['pdfName'],
                    size=data['size'],
                    s3Key=data['s3Key'],
                    status=data['status'],
                    email_title=data['email_title'],
                    email_msg=data['email_message'],
                    creator_id=user,
                    req_type=data['emailAction'],
                    expirationDateTime=data['scheduledDate'],
                    reminderDays=data['reminderDays'],
                )
                document_id = document.id

            # Create new recipients
            recipients = [
                DocumentRecipientDetail(
                    name=recipient_data['RecipientName'],
                    email=recipient_data['RecipientEmail'],
                    roleId=RecipientRole.objects.filter(
                        role_name=recipient_data["role"]
                    ).first(),
                    docId=document
                )
                for recipient_data in data['receipientData']
            ]
            DocumentRecipientDetail.objects.bulk_create(recipients)

            return JsonResponse({"doc_id": document.id, "message": "Document and recipients saved successfully."})
        else:
            return JsonResponse({"error": "Invalid request method"}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)




@csrf_exempt
def get_doc(request):
    try:
        print("doc_views get_doc")
        if request.method == 'POST':
            data = JSONParser().parse(request)
            docId = data.get('docId')

            # Check if doc_id is provided
            if not docId:
                return JsonResponse({"error": "doc_id is required"}, status=400)

            # Retrieve document by doc_id
            document = DocumentTable.objects.get(id=docId)

            # Retrieve recipient details for the document
            recipients = DocumentRecipientDetail.objects.filter(docId=document)

            # Serialize document and recipient data
            serialized_data = {
                "doc_id": document.id,
                "name": document.name,
                "pdfName": document.pdfName,
                "size": document.size,
                "s3Key": document.s3Key,
                "status": document.status,
                "email_title": document.email_title,
                "email_message": document.email_msg,
                "creator_id": document.creator_id.id,
                "req_type": document.req_type,
                "expirationDateTime": document.expirationDateTime,
                "reminderDays": document.reminderDays,
                "recipients": [
                    {
                        "RecipientName": recipient.name,
                        "RecipientEmail": recipient.email,
                        "role": recipient.roleId.role_name
                    }
                    for recipient in recipients
                ]
            }
            return JsonResponse(serialized_data)
        else:
            return JsonResponse({"error": "Invalid request method"}, status=405)
    except DocumentTable.DoesNotExist:
        return JsonResponse({"error": "Document not found"}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@log_api_request
def save_recipient_position_data(request):
    try:
        if request.method == 'POST':
            data = JSONParser().parse(request)
            newData1 = data["recipient_data"]
            Expiration = data["Expiration"]
            docId = data["docId"]
            s_send = data["s_send"]
            isSigned = data["isSigned"]
            last_modified_by_id=data["last_modified_by_id"]
            doc = DocumentTable.objects.get(pk=docId)
            doc.last_modified_by_id = last_modified_by_id
            doc.save()

            i = 0
            for newData in newData1:
                i = i+1
                doc_id = newData['docId']
                doc_recipient_detail_id = newData['docRecipientdetails_id']
                doc_recipient_detail = DocumentRecipientDetail.objects.get(pk=doc_recipient_detail_id)
                doc_Id = DocumentTable.objects.filter(
                    id = newData["docId"]
                ).first()
                rec_Id = DocumentRecipientDetail.objects.filter(
                    id = newData["docRecipientdetails_id"]
                ).first()
                RecipientPositionData.objects.create(
                    fieldName=newData['fieldName'],
                    color=newData['color'],
                    boxId=newData['boxId'],
                    pageNum=newData['pageNum'],
                    x=newData['x'],
                    y=newData['y'],
                    width=newData['width'],
                    height=newData['height'],
                    signer_status=newData['signer_status'],
                    reviewer_status=newData['reviewer_status'],
                    docId=doc_Id,
                    docRecipientdetails_id=rec_Id
                )
            email_list = DocumentRecipientDetail.objects.filter(docId=docId).values_list('email', flat=True)
            doc = DocumentTable.objects.get(pk=docId)
            reciever_panel_endpoint = config('RECIEVER_PANEL_ENDPOINT')

            email_list = list(email_list)
            recipients = DocumentRecipientDetail.objects.filter(docId=docId)
            print("recipients ====> ",recipients)
            email_messages = []
            for rec in recipients:
                if rec.roleId_id == 1:
                    url = f"{reciever_panel_endpoint}#/recieverPanel?docType=doc&type=signer&did={docId}&rid={rec.id}"
                    msg = doc.email_msg
                    message = doc.email_msg + "{reciever_panel_endpoint}#/recieverPanel?docType=doc&type=viewer&did={docId}&rid={rec.id}"
                    recRole='Sign'
                elif rec.roleId_id == 2:
                    url = f"{reciever_panel_endpoint}#/recieverPanel?docType=doc&type=viewer&did={docId}&rid={rec.id}"
                    msg = doc.email_msg
                    message = doc.email_msg + "{reciever_panel_endpoint}#/recieverPanel?docType=doc&type=viewer&did={docId}&rid={rec.id}"
                    recRole='View'
                else:
                    continue  
                email_messages.append({
                    'email': rec.email,
                    'subject': doc.email_title,
                    'message': message,
                    'msg': msg,
                    'url':url,
                    'recRole':recRole
                })

            payload = {
                "recipient_list":email_messages,
                "rdays":doc.reminderDays,
                "sdate":doc.expirationDateTime,
                "docID":docId,
                "Schedule" : data["Schedule"],
                "scheduleDateAndTime" : data["scheduleDateAndTime"]
                # "subject":doc.email_title,
                # "message":message
            }

            if doc.req_type == "S":
                print("=======================> inside save recipient")
                sequence_emails(payload,isSigned)
            elif doc.req_type == "C":
                sequence_emails(payload,isSigned)
            elif doc.req_type == "N":
                if data["Schedule"]:
                    none_send_email_schedule(email_messages,doc,data["scheduleDateAndTime"])
                else:
                    none_send_email(email_messages,doc)

            return JsonResponse({"message": "Recipient position data saved successfully.","error":False}, status=201)
        else:
            return JsonResponse({"error": "Invalid request method"}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
   
   
class DocAllRecipientById(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, Doc_id):
        try:
            print("doc_views DocAllRecipientById get")
            # Retrieve TemplateDraggedData objects based on the provided template_id
            rec_data = DocumentRecipientDetail.objects.filter(docId=Doc_id)
            serializer = DocumentRecipientSerializer(rec_data, many=True)
            return JsonResponse(serializer.data,safe=False)
        except DocumentRecipientDetail.DoesNotExist:
            return Response({"error": "Template Recipient Data not found for the given template_id"}, status=status.HTTP_404_NOT_FOUND)
 
class GetDraggedDataByDocRec(APIView):
    def get(self, request, docId,docRecipientdetails_id):
        print("doc_views GetDraggedDataByDocRec get")
        recipient_positions = RecipientPositionData.objects.filter(docId=docId, docRecipientdetails_id=docRecipientdetails_id)
        serializer = DocumentPositionSerializer(recipient_positions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# /// rajvi api for deleting recipients by document id
# class DeleteRecipientByDocIdView(APIView):
#     def delete(self, request, doc_id):
#         try:
#             recipients = DocumentRecipientDetail.objects.filter(docId=doc_id)
#             if recipients.exists():
#                 recipients.delete()
#                 return JsonResponse({"message": "Recipients deleted successfully."}, status=200)
#             else:
#                 return JsonResponse({"error": "No recipients found for the given document ID."}, status=404)
#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=500)


# send email
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
import json
 
@csrf_exempt
def send_email(request):
    if request.method == 'POST':
        myemdata = json.loads(request.body)
        recipient_emails = myemdata.get('recipient_emails')
        subject = myemdata.get('subject', '')
        message = myemdata.get('message', '')
 
        try:
            print("doc_views send_email")
            send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_emails)
            return JsonResponse({'success': True, 'message': 'Email sent successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)

def test(request):
    tasc_func.delay()
    return HttpResponse("Done")

def send_mail_to_all(request):
    send_mail_func.delay()
    return  HttpResponse("sent")

# fetching data for the UI
def get_email_list(request):
    try:
        email_list = list(EmailList.objects.values('id', 'emails', 'status'))
        return JsonResponse({'email_list': email_list}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
 



# ===================================================================================
# CELERY VIEW
# ===================================================================================  

# Mail sending orders

def none_send_email(email_messages, doc):
    try:
        for email_message in email_messages:
            recipient_email = email_message.get('email')
            subject = email_message.get('subject')
            msg = email_message.get('msg')
            message = email_message.get('message')
            url = email_message.get('url')
            username = recipient_email.split('@')[0]
            recRole = email_message.get('recRole')

            try:
                email_obj = EmailList.objects.create(emails=recipient_email, status="sent", docId=doc)
                email_obj.save()
            except Exception as e:
                return JsonResponse({'success': False, 'message': f"Error creating email entry: {str(e)}"})

            try:
                schedule_sequence_email({
                    "email": recipient_email,
                    "reminderDays": doc.reminderDays,
                    "scheduledDate": doc.expirationDateTime,
                    "doc_id": doc.id,
                    "title": subject,
                    "message": message
                })
                
                html_content = render_to_string('otp-template/document-signing.html', {
                    'reciever_link': url,
                    'username': username,
                    'message': msg,
                    'recRole': recRole
                })
                text_content = strip_tags(html_content)
                
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=settings.EMAIL_HOST_USER,
                    to=[recipient_email]
                )
                email.attach_alternative(html_content, "text/html")
                email.send()
            except Exception as e:
                return JsonResponse({'success': False, 'message': f"Error sending email: {str(e)}"})

        return JsonResponse({'success': True, 'message': 'Emails sent successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f"Unexpected error: {str(e)}"})
   
   
def none_send_email_schedule(email_messages, doc, datetime):
    try:
        print("doc_views none_send_email_schedule")
        for email_message in email_messages:
            recipient_email = email_message.get('email')
            subject = email_message.get('subject', '')
            msg = email_message.get('msg')
            message = email_message.get('message', '')
            url = email_message.get('url')
            recRole = email_message.get('recRole')
            username = recipient_email.split('@')[0]
 
            try:
                email_obj = EmailList.objects.create(emails=recipient_email, status="pending", docId=doc)
                email_obj.save()
            except Exception as e:
                print("Error creating or saving EmailList object:", e)
 
            # Generate HTML content for the email
            html_content = render_to_string('otp-template/document-signing.html', {
                'reciever_link': url,
                'username': username,
                'message': msg,
                'recRole': recRole
            })
            text_content = strip_tags(html_content)
 
            # Schedule the email
            send_mail_to_sequence_recipient_schedule(recipient_email, subject, text_content, html_content, doc.id, datetime)
 
        return JsonResponse({'success': True, 'message': 'Emails scheduled successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
 


# def send_mail_to_sequence_recipient(email_obj, subject, text_content, html_content, doc_id):
#     print("doc_views send_mail_to_sequence_recipient")
   
#     # Update the status of the current email to 'sent'
#     email_data = EmailList.objects.filter(docId=doc_id, emails=email_obj).first()
#     email_data.status = 'sent'
#     email_data.save()
   
#     from_email = settings.EMAIL_HOST_USER
   
#     # Send the email with HTML content
#     email = EmailMultiAlternatives(
#         subject=subject,
#         body=text_content,
#         from_email=from_email,
#         to=[email_obj]
#     )
#     print("send_mail_to_sequence_recipient_email",email)
#     email.attach_alternative(html_content, "text/html")
#     email.send()

def send_mail_to_sequence_recipient(email_obj, subject, text_content="", html_content="", doc_id=None):
    print("doc_views send_mail_to_sequence_recipient",email_obj," ",subject)
    
    # Update the status of the current email to 'sent'
    email_data = EmailList.objects.filter(docId=doc_id, emails=email_obj).first()

    if email_data is None:
        return JsonResponse({"error": "Email not found or already processed."}, status=404)
    
    email_data.status = 'sent'
    email_data.save()
    
    from_email = settings.EMAIL_HOST_USER
    
    # Send the email with HTML content
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=[email_obj]
    )
    print("send_mail_to_sequence_recipient_email", email)
    if html_content:  # Only attach HTML content if it is provided
        email.attach_alternative(html_content, "text/html")
    email.send()



def send_mail_to_sequence_recipient_schedule(recipient_email, subject, text_content, html_content, doc_id, scheduled_datetime):
    try:
        print("doc_views send_mail_to_sequence_recipient")
       
        if isinstance(scheduled_datetime, str):
            scheduled_datetime = datetime.strptime(scheduled_datetime, '%d/%m/%Y, %H:%M')
            scheduled_datetime = timezone.make_aware(scheduled_datetime, timezone.get_current_timezone())
       
        if isinstance(scheduled_datetime, datetime):
            expiration_days = (scheduled_datetime - timezone.now()).days
            doc = DocumentTable.objects.get(pk=doc_id)

            scheduled_email = ScheduledEmail.objects.create(
                recipient_email=recipient_email,
                scheduled_time=scheduled_datetime,
                expiration_days=expiration_days,
                doc_id=doc
            )

            crontab_schedule, created = CrontabSchedule.objects.get_or_create(
                minute=scheduled_datetime.minute,
                hour=scheduled_datetime.hour,
                day_of_month=scheduled_datetime.day,
                month_of_year=scheduled_datetime.month,
                defaults={'timezone': 'Asia/Kolkata'}
            )

            task_name = f"send_mail_to_{recipient_email.replace('@', '_').replace('.', '_')}_at_{scheduled_datetime.strftime('%Y_%m_%d_%H_%M')}"
           
            PeriodicTask.objects.update_or_create(
                name=task_name,
                defaults={
                    'crontab': crontab_schedule,
                    'task': 'send_mail_app.task.send_mail_func',
                    'args': json.dumps([scheduled_email.id, subject, text_content, html_content]),
                }
            )
    except Exception as e:
        print("Error:", e)


def sequence_emails(data,isSigned):
    try:
        recipient_list = data["recipient_list"]
        if not recipient_list:
            return JsonResponse({"success": False, "message": "Recipient list is empty"}, status=400)
        print("Save Reciepent list : ",recipient_list)
        first_recipient_sent = False
        for recipient_email in recipient_list:
            print("recipient_email ==>: ",recipient_email['email'])
            # somethinf wrong it passes not email
            doc_Id1 = DocumentTable.objects.filter(id=data["docID"]).first()
            email_obj = EmailList.objects.create(emails=recipient_email['email'], docId=doc_Id1)
           
            # Prepare email content
            username = recipient_email['email'].split('@')[0]
            html_content = render_to_string('otp-template/document-signing.html', {
                'reciever_link': recipient_email.get('url'),
                'username': username,
                'message': recipient_email.get('msg'),
                'recRole': recipient_email.get('recRole')
            })
            text_content = strip_tags(html_content)
            print("==========================>")
            if not first_recipient_sent:
                schedule_sequence_email({
                    "email": recipient_email["email"],
                    "reminderDays": data["rdays"],
                    "scheduledDate": data['sdate'],
                    "doc_id": data["docID"],
                    "title": recipient_email['subject'],
                    "message": recipient_email["message"],
                    "text_content":text_content,
                    "html_content":html_content
                })
                if data["Schedule"]:
                    send_mail_to_sequence_recipient_schedule(
                        recipient_email['email'],
                        recipient_email['subject'],
                        text_content,
                        html_content,
                        data["docID"],
                        data["scheduleDateAndTime"]
                    )
                else:
                    send_mail_to_sequence_recipient(
                        recipient_email['email'],
                        recipient_email['subject'],
                        text_content,
                        html_content,
                        data["docID"]
                    )
                
                # add condition for sending schedule email 
                if isSigned["isSignedStatus"]:
                    first_recipient_sent = False
                    email_obj = EmailList.objects.filter(docId=data["docID"], emails=isSigned["email"]).first()
                    if email_obj:
                        email_obj.status = 'approved'
                        email_obj.save()
                else:
                    first_recipient_sent = True
            else:
                email_obj.save()

        return JsonResponse({"success": True, "message": "Emails sent successfully"}, safe=False)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


@csrf_exempt
@require_POST
def sequence_email_approval(request):
    try:
        data = JSONParser().parse(request)
        doc_id = data["doc_id"]
        rid = data["email_id"]
        lastModID = data["lastModID"]
        reciever_panel_endpoint = config('RECIEVER_PANEL_ENDPOINT')

        doc = DocumentTable.objects.get(pk=doc_id)
        doc.last_modified_by_id = lastModID
        doc.save()
        email_id = DocumentRecipientDetail.objects.filter(id=rid, docId=doc_id).first()
       
        if doc.req_type == "S":
            if email_id:
                email_obj = EmailList.objects.filter(docId=doc_id, emails=email_id.email).first()
                if email_obj and email_obj.status == 'sent':
                    email_obj.status = 'approved'
                    email_obj.save()
                   
                    next_pending_email = EmailList.objects.filter(status='pending', docId=doc_id).first()
                    if next_pending_email:
                        recipients = DocumentRecipientDetail.objects.filter(docId=doc_id, email=next_pending_email.emails).first()
                        if recipients.roleId.role_id == 1:
                            url = f"{reciever_panel_endpoint}#/recieverPanel?docType=doc&type=signer&did={doc_id}&rid={recipients.id}"
                            message = doc.email_msg + f"\n\nThank you for choosing Signakshar. Click on the following link for signing the document: {url} \nIgnore this reminder if you have already signed the document."
                        elif recipients.roleId.role_id == 2:
                            url = f"{reciever_panel_endpoint}#/recieverPanel?docType=doc&type=viewer&did={doc_id}&rid={recipients.id}"
                            message = doc.email_msg + f"\n\nThank you for choosing Signakshar. Click on the following link for viewing the pdf: {url} \nIgnore this reminder if you have already viewed the document."
                       
                        role_descriptions = {1: "Sign", 2: "View"}# Inside the for loop where you render HTML content:
                        role_action = role_descriptions.get(recipients.roleId.role_id, "view")  # Default to "view" if role_id not found

                        # Render HTML content
                        username = next_pending_email.emails.split('@')[0]
                        html_content = render_to_string('otp-template/document-signing.html', {
                            'reciever_link': url,
                            'username': username,
                            'document_action': role_action,  # Use the mapped action
                            'recRole': role_action
                        })
                        text_content = strip_tags(html_content)
                        # print("seuqnce_email_Approval_textcontent_S",text_content)

                        schedule_sequence_email({
                            "email": next_pending_email.emails,
                            "reminderDays": doc.reminderDays,
                            "scheduledDate": doc.expirationDateTime,
                            "doc_id": doc_id,
                            "title": doc.email_title,
                            "text_content":text_content,
                            "html_content":html_content,
                            # "message": message
                        })
                        send_mail_to_sequence_recipient(
                            next_pending_email.emails,
                            doc.email_title,
                            text_content,
                            html_content,
                            doc_id
                        )
                        return JsonResponse({"success": "Next recipient notified"}, safe=False, status=200)
                    else:
                        doc.status = "Completed"
                        doc.save()
                        return JsonResponse({"success": "Document approved successfully", "last_approved": True}, safe=False, status=200)
                else:
                    return JsonResponse({"error": "Email has already been sent or not found..!!"}, status=400)
            else:
                return JsonResponse({"error": "Recipient data not found..!!"}, status=404)
       
        elif doc.req_type == "N":
            if email_id:
                email_obj = EmailList.objects.filter(docId=doc_id)
                for data in email_obj:
                    if data.emails == email_id.email and data.status == 'sent':
                        data.status = 'approved'
                        data.save()
               
                email_obj = EmailList.objects.filter(docId=doc_id)
                all_approved = all(data.status == 'approved' for data in email_obj)
               
                if all_approved:
                    doc.status = "Completed"
                    doc.save()
                    return JsonResponse({"success": "Document complete!!", "last_approved": True}, status=200)
                return JsonResponse({"success": True}, safe=False, status=200)
            else:
                return JsonResponse({"error": "Recipient data not found..!!"}, status=404)
       
        elif doc.req_type == "C":
            if email_id:
                email_obj = EmailList.objects.filter(docId=doc_id, emails=email_id.email).first()
                if email_obj and email_obj.status == 'sent':
                    email_obj.status = 'approved'
                    email_obj.save()
                   
                    next_pending_email = EmailList.objects.filter(status='pending', docId=doc_id)
                    for data in next_pending_email:
                        recipients = DocumentRecipientDetail.objects.filter(docId=doc_id, email=data.emails).first()
                        if not recipients:
                            continue

                        if recipients.roleId.role_id == 1:
                            url = f"{reciever_panel_endpoint}#/recieverPanel?docType=doc&type=signer&did={doc_id}&rid={recipients.id}"
                            message = doc.email_msg + f"\n\nThank you for choosing Signakshar. Click on the following link for signing the document: {url} \nIgnore this reminder if you have already signed the document."
                        elif recipients.roleId.role_id == 2:
                            url = f"{reciever_panel_endpoint}#/recieverPanel?docType=doc&type=viewer&did={doc_id}&rid={recipients.id}"
                            message = doc.email_msg + f"\n\nThank you for choosing Signakshar. Click on the following link for viewing the pdf: {url} \nIgnore this reminder if you have already viewed the document."
                        
                        role_descriptions = {1: "Sign", 2: "View"}# Inside the for loop where you render HTML content:
                        role_action = role_descriptions.get(recipients.roleId.role_id, "view")  # Default to "view" if role_id not found

                        # Render HTML content
                        username = data.emails.split('@')[0]
                        html_content = render_to_string('otp-template/document-signing.html', {
                            'reciever_link': url,
                            'username': username,
                            'document_action': role_action,  # Use the mapped action
                            'recRole': role_action
                        })
                        text_content = strip_tags(html_content)
                        # print("seuqnce_email_Approval_textcontent_C",text_content)

                        schedule_sequence_email({
                            "email": data.emails,
                            "reminderDays": doc.reminderDays,
                            "scheduledDate": doc.expirationDateTime,
                            "doc_id": doc_id,
                            "title": doc.email_title,
                            "text_content":text_content,
                            "html_content":html_content
                            # "message": message
                        })
                        send_mail_to_sequence_recipient(
                            data.emails,
                            doc.email_title,
                            text_content,
                            html_content,
                            doc_id
                        )

                    email_obj = EmailList.objects.filter(docId=doc_id)
                    all_approved = all(data.status == 'approved' for data in email_obj)

                    if all_approved:
                        doc.status = "Completed"
                        doc.save()
                        return JsonResponse({"success": "Document complete!!", "last_approved": True}, status=200)
                    return JsonResponse({"success": "Emails sent successfully."}, status=200)
                else:
                    return JsonResponse({"error": "Email has already been sent or not found..!!"}, status=400)
            else:
                return JsonResponse({"error": "Recipient data not found..!!"}, status=404)

        else:
            return JsonResponse({"error": "No method of req_type found ..!!"}, status=404)

    except DocumentTable.DoesNotExist:
        return JsonResponse({"error": "Document not found"}, status=404)
    except EmailList.DoesNotExist:
        return JsonResponse({"error": "Email not found"}, status=404)
    except Exception as e:
        print("Exception occurred:", str(e))
        return JsonResponse({"error": str(e)}, status=400)


# def schedule_sequence_email(data):
#     try:
#         print("doc_views schedule_sequence_email")
#         print("==================1===========================")
#         recipient_email = data['email']
#         scheduled_date = data['scheduledDate']
#         print("scheduled_date : ",type(scheduled_date))
#         reminder_days = data['reminderDays']
#         doc_id = data['doc_id']
#         message = data['message']
#         title = data['title']
#         html_content = data.get('html_content', '')
#         text_content = strip_tags(html_content)
#         print("====================2=========================")
#         if isinstance(scheduled_date, str):
#             # If scheduled_date is a string, parse it to a datetime object
#             scheduled_datetime = datetime.strptime(scheduled_date, '%Y-%m-%d %H:%M:%S%z')
#         elif isinstance(scheduled_date, datetime):
#             # If scheduled_date is already a datetime object, use it directly
#             scheduled_datetime = scheduled_date
#         else:
#             raise ValueError("scheduled_date is neither a string nor a datetime object")

#         # Format the datetime object as per the required format
#         formatted_date = scheduled_datetime.strftime('%d-%m-%Y')
#         print("Formatted scheduled_date:", formatted_date)

#         # Parse the string to a datetime object
       
#         scheduled_datetime = timezone.make_aware(datetime.strptime(formatted_date,'%d-%m-%Y'), timezone.get_current_timezone())
#         print("===================3==========================")
#         # Calculate the reminder date for 4:00:00 PM
#         reminder_datetime_pm = scheduled_datetime - timedelta(days=1)
#         reminder_datetime_pm = reminder_datetime_pm.replace(hour=14, minute=2, second=0)
#         print("===================4==========================")
#         # Calculate the reminder date for 10:00:00 AM based on selected days--------change hereeeeeeeeeeeeeee
#         reminder_datetime_am = scheduled_datetime - timedelta(days=reminder_days)
#         reminder_datetime_am = reminder_datetime_am.replace(hour=13, minute=54, second=0)
#         print("===================5==========================")
#         expiration_days = (scheduled_datetime - timezone.now()).days
#         doc = DocumentTable.objects.get(pk=doc_id)
#         print("===================6==========================")
#         print(doc)
#         scheduled_email = ScheduledEmail.objects.create(
#             recipient_email=recipient_email,
#             scheduled_time=scheduled_datetime,
#             expiration_days=expiration_days,
#             reminder_date_pm=reminder_datetime_pm,
#             reminder_date_am=reminder_datetime_am,
#             doc_id=doc
#         )
#         print("==================***********************************************==")
#         # Create CrontabSchedules for both reminder times
#         crontab_schedule_pm, created_pm = CrontabSchedule.objects.get_or_create(
#             minute=2,
#             hour=14,
#             day_of_month=reminder_datetime_pm.day,
#             month_of_year=reminder_datetime_pm.month,
#             defaults={'timezone': 'Asia/Kolkata'}
#         )
#         # //////////////////change hereeeeeee
#         crontab_schedule_am, created_am = CrontabSchedule.objects.get_or_create(
#             minute=54,
#             hour=13,
#             day_of_month=reminder_datetime_am.day,
#             month_of_year=reminder_datetime_am.month,
#             defaults={'timezone': 'Asia/Kolkata'}
#         )
#         print("==================***********************************************==")
#         # Create PeriodicTasks associated with the scheduled email and CrontabSchedules
#         task_name_pm = f"send_mail_to_{recipient_email.replace('@', '_').replace('.', '_')}_at_{reminder_datetime_pm.strftime('%Y_%m_%d_%H_%M')}_pm"
#         task_name_am = f"send_mail_to_{recipient_email.replace('@', '_').replace('.', '_')}_at_{reminder_datetime_am.strftime('%Y_%m_%d_%H_%M')}_am"
#         print("==================***********************************************==")
#         # Update or create PeriodicTasks for 4:00:00 PM reminder
#         PeriodicTask.objects.update_or_create(
#             name=task_name_pm,
#             defaults={
#                 'crontab': crontab_schedule_pm,
#                 'task': 'send_mail_app.task.send_mail_func',
#                 'args': json.dumps([scheduled_email.id,title,text_content, html_content]),
#             }
#         )
   
#         # Update or create PeriodicTasks for 10:00:00 AM reminder
#         PeriodicTask.objects.update_or_create(
#             name=task_name_am,
#             defaults={
#                 'crontab': crontab_schedule_am,
#                 'task': 'send_mail_app.task.send_mail_func',
#                 'args': json.dumps([scheduled_email.id,title,text_content,html_content]),
#             }
#         )

#         return JsonResponse({'message': 'Scheduled Email'}, status=200)
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)


def schedule_sequence_email(data):
    try:
        print("doc_views schedule_sequence_email",data['email'])
        recipient_email = data['email']
        scheduled_date = data['scheduledDate']
        reminder_days = data['reminderDays']
        doc_id = data['doc_id']
        message = data['message']
        title = data['title']
        html_content = data.get('html_content', '')
        text_content = strip_tags(html_content)

        if isinstance(scheduled_date, str):
            # If scheduled_date is a string, parse it to a datetime object
            scheduled_datetime = datetime.strptime(scheduled_date, '%Y-%m-%d %H:%M:%S%z')
        elif isinstance(scheduled_date, datetime):
            # If scheduled_date is already a datetime object, use it directly
            scheduled_datetime = scheduled_date
        else:
            raise ValueError("scheduled_date is neither a string nor a datetime object")

        # Format the datetime object as per the required format
        formatted_date = scheduled_datetime.strftime('%d-%m-%Y')

        # Parse the string to a datetime object
        scheduled_datetime = timezone.make_aware(datetime.strptime(formatted_date, '%d-%m-%Y'), timezone.get_current_timezone())

        # Calculate the reminder date for 4:00:00 PM
        reminder_datetime_pm = scheduled_datetime - timedelta(days=1)
        reminder_datetime_pm = reminder_datetime_pm.replace(hour=15, minute=57, second=0)

        # Calculate the reminder date for 10:00:00 AM based on selected days
        reminder_datetime_am = scheduled_datetime - timedelta(days=reminder_days)
        reminder_datetime_am = reminder_datetime_am.replace(hour=16, minute=22, second=0)

        expiration_days = (scheduled_datetime - timezone.now()).days
        doc = DocumentTable.objects.get(pk=doc_id)

        scheduled_email = ScheduledEmail.objects.create(
            recipient_email=recipient_email,
            scheduled_time=scheduled_datetime,
            expiration_days=expiration_days,
            reminder_date_pm=reminder_datetime_pm,
            reminder_date_am=reminder_datetime_am,
            doc_id=doc
        )

        # Create CrontabSchedules for both reminder times
        crontab_schedule_pm, created_pm = CrontabSchedule.objects.get_or_create(
            minute=57,
            hour=15,
            day_of_month=reminder_datetime_pm.day,
            month_of_year=reminder_datetime_pm.month,
            defaults={'timezone': 'Asia/Kolkata'}
        )

        crontab_schedule_am, created_am = CrontabSchedule.objects.get_or_create(
            minute=22,
            hour=16,
            day_of_month=reminder_datetime_am.day,
            month_of_year=reminder_datetime_am.month,
            defaults={'timezone': 'Asia/Kolkata'}
        )

        # Create PeriodicTasks associated with the scheduled email and CrontabSchedules
        task_name_pm = f"send_mail_to_{recipient_email.replace('@', '_').replace('.', '_')}_at_{reminder_datetime_pm.strftime('%Y_%m_%d_%H_%M')}_pm"
        task_name_am = f"send_mail_to_{recipient_email.replace('@', '_').replace('.', '_')}_at_{reminder_datetime_am.strftime('%Y_%m_%d_%H_%M')}_am"

        # Update or create PeriodicTasks for 4:00:00 PM reminder
        PeriodicTask.objects.update_or_create(
            name=task_name_pm,
            defaults={
                'crontab': crontab_schedule_pm,
                'task': 'send_mail_app.task.send_mail_func',
                'args': json.dumps([scheduled_email.id, title, text_content, html_content]),
            }
        )

        # Update or create PeriodicTasks for 10:00:00 AM reminder
        PeriodicTask.objects.update_or_create(
            name=task_name_am,
            defaults={
                'crontab': crontab_schedule_am,
                'task': 'send_mail_app.task.send_mail_func',
                'args': json.dumps([scheduled_email.id, title, text_content, html_content]),
            }
        )

        return JsonResponse({'message': 'Scheduled Email'}, status=200)

    except Exception as e:
        print("Exception occurred in schedule_sequence_email:", str(e))
        return JsonResponse({'error': str(e)}, status=500)



from send_mail_app.task import delete_expired_documents

@csrf_exempt
def trigger_delete_expired_documents(request):
    print("doc_views trigger_delete_expired_documents")
    if request.method == 'POST':
        delete_expired_documents.delay()  # Trigger the Celery task asynchronously
        return JsonResponse({'message': 'Task to delete expired documents has been triggered.'})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


