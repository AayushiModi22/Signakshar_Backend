from django.forms import ValidationError
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from .serializers import UserSerializer,TemplateSerializer,TemplateDraggedSerializer ,TemplateRecipientSerializer,DocumentTableSerializer,UseTemplateRecipientSerializer,DocumentRecipientSerializer,DocumentPositionSerializer,DocumentSerializer,UserInitialsSerializer,UserSignatureSerializer
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import User
#library: pip install PyJWT
from datetime import datetime
import jwt
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from social_django.utils import psa
from django.views.decorators.csrf import csrf_exempt
from .models import Template,TemplateDraggedData,TemplateRecipient,DocumentTable,UseTemplateRecipient,otpUser,DocumentRecipientDetail,RecipientRole,RecipientPositionData, Signature, Initials,BulkPdfDocumentTable,BulkPdfPositionData,BulkPdfRecipientDetail
from datetime import datetime, timedelta
from send_mail_app.models import EmailList
from send_mail_app.serializers import EmailListSerializer
from django.db.models import Q
 
# @csrf_exempt
class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get('Authorization', None)
 
        if not token:
            return None
 
        try:
            # Extracting JWT token from Bearer headers
            token = token.split(' ')[1]
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
 
        user = User.objects.filter(id=payload.get('id')).first()
        if user is None:
            raise AuthenticationFailed('User not found!')
 
        return (user, token)
 

class Registerview(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_user = serializer.save()
        uid = new_user.id
        try:
            data = request.data
            signature_data = {
                # 'id': uid,
                'draw_img_name': data.get('draw_img_name_signature'),
                'draw_enc_key': data.get('draw_enc_key'),
                'img_name': data.get('img_name_signature'),
                'img_enc_key': data.get('img_enc_key'),
                'user_id_id': new_user.id,
            }
            initial_data = {
                # 'id': new_user.id,
                'draw_img_name': data.get('draw_img_name_initials'),
                'draw_enc_key': data.get('draw_enc_key'),
                'img_name': data.get('img_name_initials'),
                'img_enc_key': data.get('img_enc_key'),
                'user_id_id': new_user.id,
            }
 
            signatureTableData = Signature.objects.create(**signature_data)
            initialTableData = Initials.objects.create(**initial_data)
           
        except KeyError as e:
            return JsonResponse({'error': str(e)}, status=400)
 
        return Response(serializer.data)
 
 
 
class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']
 
        user = User.objects.filter(email=email).first()
 
        if user is None:
            raise AuthenticationFailed('User not found!')
        if user.signIn_with_google=="Y":
            raise AuthenticationFailed('You have loged in with google!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')
       
        payload = {
            'id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=24),  # Use datetime.utcnow() for JWT standard
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, 'secret', algorithm='HS256')
 
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {'jwt': token}
        return response
    
 
class logoutview(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {'message': 'success'}
        return response
 
class UserView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
 
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
       
        userSignatueDetails = Signature.objects.filter(user_id_id=serializer.data["id"]).first()        
        userInitialsDetails = Initials.objects.filter(user_id_id=serializer.data["id"]).first()
 
        signature_serializer = UserSignatureSerializer(userSignatueDetails) if userSignatueDetails else None
        initials_serializer = UserInitialsSerializer(userInitialsDetails) if userInitialsDetails else None
 
        response_data = {
            'user': serializer.data,
            'signature_details': signature_serializer.data if signature_serializer else None,
            'initials_details': initials_serializer.data if initials_serializer else None
        }
        return Response(response_data)
 

from rest_framework.parsers import MultiPartParser, FormParser

class UserUpdateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request):
        user = request.user
        
        user_data = {
            'full_name': request.data.get('user[full_name]'),
            'initial': request.data.get('user[initial]'),
            'profile_pic': request.data.get('user[profile_pic]')
        }
        signature_data = {
            'draw_img_name': request.data.get('signature[draw_img_name]'),
            'draw_enc_key': request.data.get('signature[draw_enc_key]'),
            'img_name': request.data.get('signature[img_name]'),
            'img_enc_key': request.data.get('signature[img_enc_key]')
        }
        initials_data = {
            'draw_img_name': request.data.get('initials[draw_img_name]'),
            'draw_enc_key': request.data.get('initials[draw_enc_key]'),
            'img_name': request.data.get('initials[img_name]'),
            'img_enc_key': request.data.get('initials[img_enc_key]')
        }

        user_serializer = UserSerializer(user, data=user_data, partial=True)
        signature_queryset = Signature.objects.filter(user_id=user)
        initials_queryset = Initials.objects.filter(user_id=user)

        if signature_queryset.exists():
            signature_instance = signature_queryset.first()
        else:
            signature_instance = Signature(user_id=user)

        if initials_queryset.exists():
            initials_instance = initials_queryset.first()
        else:
            initials_instance = Initials(user_id=user)

        signature_serializer = UserSignatureSerializer(signature_instance, data=signature_data, partial=True)
        initials_serializer = UserInitialsSerializer(initials_instance, data=initials_data, partial=True)

        try:
            if user_serializer.is_valid():
                user_serializer.save()

                if signature_serializer.is_valid():
                    signature_serializer.save()
                else:
                    raise ValidationError(signature_serializer.errors)

                if initials_serializer.is_valid():
                    initials_serializer.save()
                else:
                    raise ValidationError(initials_serializer.errors)

                return Response({
                    'user': user_serializer.data,
                    'signature': signature_serializer.data,
                    'initials': initials_serializer.data
                }, status=status.HTTP_200_OK)
            else:
                raise ValidationError(user_serializer.errors)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class FetchUserDetailsView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            user_serializer = UserSerializer(user)

            user_signature_details = Signature.objects.filter(user_id_id=user_id).first()
            user_initials_details = Initials.objects.filter(user_id_id=user_id).first()

            signature_serializer = UserSignatureSerializer(user_signature_details) if user_signature_details else None
            initials_serializer = UserInitialsSerializer(user_initials_details) if user_initials_details else None

            response_data = {
                'user': user_serializer.data,
                'signature_details': signature_serializer.data if signature_serializer else None,
                'initials_details': initials_serializer.data if initials_serializer else None
            }

            return Response(response_data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found!'}, status=status.HTTP_404_NOT_FOUND)


from rest_framework import status
from rest_framework.response import Response
 
class TemplateViewSet(viewsets.ModelViewSet):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
 
    def get_queryset(self):
        user = self.request.user
        queryset = Template.objects.filter(created_by=user)
 
        return queryset
 
    def create(self, request, *args, **kwargs):
        template_name = request.data.get('templateName')
        userid = request.data.get('created_by')
 
        existing_template = Template.objects.filter(
            templateName=template_name, created_by=userid
        ).exists()
 
        if existing_template:
            return Response(
                {"error": "Template with the same name already exists for this user."}
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
class TemplateDraggedDataViewset(viewsets.ModelViewSet):
    queryset=TemplateDraggedData.objects.all()
    serializer_class=TemplateDraggedSerializer
 
class GetDraggedDataByTempRec(APIView):
    def get(self, request, template_rec_id):
        template_rec = get_object_or_404(TemplateRecipient, id=template_rec_id)
        dragged_data = TemplateDraggedData.objects.filter(templateRec=template_rec)
        serializer = TemplateDraggedSerializer(dragged_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
 
 
class TemplateRecipientViewset(viewsets.ModelViewSet):
    queryset=TemplateRecipient.objects.all()
    serializer_class=TemplateRecipientSerializer
 
class UseTemplateRecipientViewSet(viewsets.ModelViewSet):
    queryset= UseTemplateRecipient.objects.all()
    serializer_class=UseTemplateRecipientSerializer
 
from rest_framework.decorators import api_view
 
@csrf_exempt
@api_view(['GET'])
def use_template_recipient_didTidCid(request, document_id, template_id, creator_id):
    try:
        use_template_recipients = UseTemplateRecipient.objects.filter(
            docid=document_id,
            template_id=template_id,
            created_by=creator_id
        )
        serializer = UseTemplateRecipientSerializer(use_template_recipients, many=True)
        return Response(serializer.data)
    except UseTemplateRecipient.DoesNotExist:
        return Response({"error": "UseTemplateRecipient data not found for the given criteria"}, status=status.HTTP_404_NOT_FOUND)
 
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
 
 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import TemplateDraggedData
from .serializers import TemplateDraggedSerializer
from django.db.models import Q
from django.http import JsonResponse
 
class TemplateRecipientByTemplateId(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, template_id):
        try:
            # Retrieve TemplateDraggedData objects based on the provided template_id
            rec_data = TemplateRecipient.objects.filter(template_id=template_id)
            serializer = TemplateRecipientSerializer(rec_data, many=True)
            return JsonResponse(serializer.data,safe=False)
        except TemplateRecipient.DoesNotExist:
            return Response({"error": "Template Recipient Data not found for the given template_id"}, status=status.HTTP_404_NOT_FOUND)
 
 
class TemplateByTemplateId(APIView):
    # authentication_classes = [JWTAuthentication]  
    # permission_classes = [IsAuthenticated]
    def get(self, request, template_id):
        try:
            # Retrieve Template object based on the provided template_id
            template_data = Template.objects.get(template_id=template_id)
            serializer = TemplateSerializer(template_data)
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        except Template.DoesNotExist:
            return JsonResponse({"error": "Template Data not found for the given template_id"}, status=status.HTTP_404_NOT_FOUND)
       
 
class DocumentByDocId(APIView):
    # authentication_classes = [JWTAuthentication]  
    # permission_classes = [IsAuthenticated]
    def get(self, request, doc_id):
        try:
            # Retrieve Template object based on the provided template_id
            doc_data = DocumentTable.objects.get(id=doc_id)
            serializer = DocumentTableSerializer(doc_data)
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        except Template.DoesNotExist:
            return JsonResponse({"error": "Document Data not found for the given document_id"}, status=status.HTTP_404_NOT_FOUND)
               
class deleteTemplate(APIView):
    def post(self, request):
        templateID = request.data.get('templateID')
        if not templateID:
            return Response({"error": "Template ID not provided"}, status=status.HTTP_400_BAD_REQUEST)
        template = get_object_or_404(Template, template_id=templateID)
        template.delete()
        return Response({"message": "Template deleted successfully","status":200}, status=status.HTTP_200_OK)

from rest_framework.decorators import api_view
@csrf_exempt
@api_view(['PUT'])
def updateTemplateDraggedData(request, pk):
    try:
        dragged_data = TemplateDraggedData.objects.get(pk=pk)
    except TemplateDraggedData.DoesNotExist:
        return Response({"error": "Template Dragged Data not found"}, status=status.HTTP_404_NOT_FOUND)
 
    serializer = TemplateDraggedSerializer(dragged_data, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data)
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
@csrf_exempt
def login(request):
    return render(request, 'SignInForm.js')
 
@csrf_exempt
@psa('social:complete')
def google_auth(request, backend):
    """Google OAuth2 authentication handler"""
    # This function is called by the OAuth2 provider (Google) after authentication
    return redirect('/')
 
@csrf_exempt
@psa('social:complete')
def google_auth_callback(request, backend):
    """
    Google OAuth2 authentication callback handler
    This function is called by the OAuth2 provider (Google) after authentication
    """
    return redirect('/')
 
# ===================================================================================
# otp
# ===================================================================================
from django.views.decorators.http import require_POST
import random
import string
 
def send_emailnew(recipient,subject,message):
    try:
        send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient])
        return True
    except Exception as e:
        return False
 
# def generate_otp():
#     otp = ''.join(random.choices(string.digits, k=6))
#     return otp
 
# @csrf_exempt
# @require_POST
# def sendOtp(request):
#     try:
#         data = json.loads(request.body)
#         recipient_email = data.get('email', '')
#         if not recipient_email:
#             raise ValueError('Recipient email is required')
#         verified_users = otpUser.objects.filter(email=recipient_email, status='N', entry_date__gte=timezone.now() - timedelta(minutes=5))
#         if verified_users.exists():
#             return JsonResponse({'success': False, 'message': 'New OTP will be generated after 2 min.!!'})
#         verified_users_new = otpUser.objects.filter(email=recipient_email, status='Y', entry_date__gte=timezone.now() - timedelta(minutes=5))
#         if verified_users_new.exists():
#             return JsonResponse({'success': False, 'message': 'User already verified but still you can request after 2 min..!!'})
#         otp = generate_otp()
#         subject = "One time Password (OTP)"
#         message = f"Otp = {otp}"
#         response_email = send_emailnew(recipient_email, subject, message)
#         if response_email:
#             email = otpUser.objects.create(email=recipient_email, otp=otp, status='N')
#             return JsonResponse({'success': True, 'message': 'Email sent successfully'})
#         else:
#             return JsonResponse({'success': False, 'message': "Email not sent"})
#     except Exception as e:
#         return JsonResponse({'success': False, 'message': str(e)})
 
 
# @csrf_exempt
# @require_POST
# def verifyOtp(request):
#     try:
#         data = json.loads(request.body)
#         email = data.get('email', '')
#         otp = data.get('otp', '')
#         if not email:
#             return JsonResponse({'error': 'Email ID is required'}, status=400)
#         if not otp:
#             return JsonResponse({'error': 'OTP is required'}, status=400)
#         # Check if the user is already verified within the last 5 minutes
#         verified_users = otpUser.objects.filter(email=email, status='Y', entry_date__gte=timezone.now() - timedelta(minutes=5))
#         if verified_users.exists():
#             return JsonResponse({'success': False, 'message': 'User already verified..!!'})
#         user = otpUser.objects.get(email=email, status='N', otp=otp)
#         current_time = timezone.now()
#         if user.entry_date < current_time - timedelta(minutes=5):
#             return JsonResponse({'success': False, 'message': 'OTP verification failed. OTP expired.'}, status=400)
#         user.status = 'Y'
#         user.save()
#         return JsonResponse({'success': True, 'message': 'OTP verified successfully'})
#     except otpUser.DoesNotExist:
#         return JsonResponse({'success': False, 'message': 'OTP verification failed. Invalid email, OTP, or status.'}, status=400)
#     except Exception as e:
#         return JsonResponse({'success': False, 'message': str(e)}, status=500)
 
@csrf_exempt
@api_view(["POST"])
def sendOtp(request):
    body_data = request.data
    new_OTP = generate_otp()
    try:
        if not body_data["email"]:
            return Response({
                'Status':400,
                'StatusMsg':"Email is required..!!"
            })
       
        emailExistInComapny = User.objects.filter(email = body_data["email"])
 
        if not filter:
            if(emailExistInComapny):
                return Response({
                    'Status':400,
                    'StatusMsg':"This email already register..!!"
                })
        
        if filter == "F":
            if not emailExistInComapny:
                return Response({
                    'Status':400,
                    'StatusMsg':"User not register..!!"
                })
       
        try:
            OTPEntry = otpUser.objects.get(email = body_data["email"])
            OTPEntry.otp = new_OTP
            OTPEntry.status="N"
            OTPEntry.entry_date= timezone.now()
            OTPEntry.save()
 
 
 
        except otpUser.DoesNotExist :
            OTPEntry = otpUser.objects.create(email = body_data["email"],otp = new_OTP, status = "N")
    except Exception as e:
        return Response({
            'Status': 400,
            'StatusMsg': "Error while sending OTP: " + str(e)
        })  
 
       
 
    if(OTPEntry):
        # email_thread = threading.Thread(target=Send_OTP,args=(body_data["E_Mail"],"TEST","OTP : "+new_OTP))
        # email_thread.start()
        subject = "One time Password (OTP)"
        message = f"Otp = {new_OTP}"
        response_email = send_emailnew(body_data["email"], subject, message)
        # if response_email:
        #     email = otpUser.objects.create(email=body_data["email"], otp=new_OTP, status='N')
        #     return JsonResponse({'success': True, 'message': 'Email sent successfully'})
        # else:
        #     return JsonResponse({'success': False, 'message': "Email not sent"})
        return Response({
            'Status':200,
            'StatusMsg':"OTP send successfully..!!"
        })
   
    return Response({
        'Status':400,
        'StatusMsg':"Error while sending OTP..!!"
    })
 
def generate_otp():
    otp = ''.join(random.choices(string.digits, k=6))
    return otp
 
   
 
@csrf_exempt
@api_view(["POST"])
def verifyOtp(request):
    body_data = request.data
 
    try:
        if not body_data["email"]:
            return Response({
                'Status':400,
                'StatusMsg':"Email is required..!!"
            })
        if not body_data["otp"]:
            return Response({
                'Status':400,
                'StatusMsg':"OTP is required..!!"
            })
 
        OTPEntry = otpUser.objects.get(email = body_data["email"], otp = body_data["otp"])
       
        if(OTPEntry.status == "Y"):
            return Response({
                'Status':200,
                'StatusMsg':"OTP already veryfied..!!"
            })
       
        time_difference = timezone.now() - OTPEntry.entry_date
        if time_difference.total_seconds() > 300:  # 5 minutes = 300 seconds
            return Response({
                'Status': 400,
                'StatusMsg': "OTP has expired..!!"
            })
       
        OTPEntry.status = "Y"
        OTPEntry.save()
       
        return Response({
            'Status':200,
            'StatusMsg':"OTP veryfied..!!"
        })
    except otpUser.DoesNotExist:
        return Response({
            'Status':400,
            'StatusMsg':"Invalid Email or OTP ..!!"
        })
 
@csrf_exempt
@require_POST
def forgetPassword(request):
    try:
        data = json.loads(request.body)
        email = data.get('email', '')
        newPassword = data.get('newPassword', '')
        if not email:
            return JsonResponse({'error': 'Email ID is required'}, status=400)
        if not newPassword:
            return JsonResponse({'error': 'New Password is required'}, status=400)
        user = User.objects.get(email=email)
        if not user:
            return JsonResponse({'success': False, 'message': 'User not registered..!!'})

        otp_record = otpUser.objects.filter(email=email).first()
        if otp_record:
            user.set_password(newPassword)
            user.save()
            otp_record.delete()
            return JsonResponse({'success': True, 'message': 'New Password Generated..!!'})
        return JsonResponse({'success': False, 'message': 'New Password Generating failed'})
    except otpUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'New Password Generating failed. Invalid email, OTP, or status.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
 
# ===================================================================================
# aws
# ===================================================================================
import boto3
from django.http import JsonResponse
 
#  ///////////old code to just upload file in fixed bucket
# @csrf_exempt
# def upload_file_to_s3(request):
   
#     if request.method == 'POST':
#         file_object = request.FILES.get('file')
#         bucket_name = 'bucketpdfdoc'
#         print("file_object : ",file_object)
#         if not file_object or not bucket_name:
#             return JsonResponse({'success': False, 'error': 'File or bucket name not provided'}, status=400)
 
#         # Create an S3 client
#         s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#                           aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
#                           region_name=settings.AWS_REGION)
#         # Upload file to S3 bucket
#         try:
#             s3.upload_fileobj(file_object, bucket_name, file_object.name)
#             return JsonResponse({'success': True, 'message': 'File uploaded successfully'})
#         except Exception as e:
#             return JsonResponse({'success': False, 'error': str(e)}, status=500)
#     else:
#         return JsonResponse({'error': 'Method not allowed'}, status=405)
 

# ///// this code is used to create bucket and upload file
# @csrf_exempt
# def upload_file_to_s3(request):
#     if request.method == 'POST':
#         file_object = request.FILES.get('file')
#         user_id = request.POST.get('user_id')
#         user_email = request.POST.get('user_email')

#         if not file_object or not user_id or not user_email:
#             return JsonResponse({'success': False, 'error': 'File, user ID, or user email not provided'}, status=400)

#         # Extract the part of the email before the @ symbol
#         trimmed_email = user_email.split('@')[0]

#         # Generate a dynamic bucket name based on user ID and trimmed email
#         bucket_name = f'sign-{user_id}-{trimmed_email}'

#         # Create an S3 client
#         s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#                           aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
#                           region_name=settings.AWS_REGION)

#         try:
#             # Check if the bucket already exists
#             if not bucket_exists(s3, bucket_name):
#                 # Create a new bucket
#                 s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': settings.AWS_REGION})

#             # Upload file to the new bucket
#             s3.upload_fileobj(file_object, bucket_name, file_object.name)
#             return JsonResponse({'success': True, 'message': 'File uploaded successfully'})
#         except Exception as e:
#             return JsonResponse({'success': False, 'error': str(e)}, status=500)
#     else:
#         return JsonResponse({'error': 'Method not allowed'}, status=405)

# def bucket_exists(s3, bucket_name):
#     try:
#         s3.head_bucket(Bucket=bucket_name)
#         return True
#     except boto3.exceptions.botocore.client.ClientError as e:
#         error_code = int(e.response['Error']['Code'])
#         if error_code == 404:
#             return False
#         else:
#             raise

# /////////////////////now making two api one for creating bucket and another for uploading pdf in particular bucket
# import re
# import boto3
# from django.conf import settings
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt
# def create_bucket(request):
#     if request.method == 'POST':
#         user_id = request.POST.get('user_id')
#         user_email = request.POST.get('user_email')
#         if not user_id or not user_email:
#             return JsonResponse({'success': False, 'error': 'User ID or user email not provided'}, status=400)

#         # Extract the part of the email before the @ symbol
#         trimmed_email = user_email.split('@')[0].lower()
#         # Replace invalid characters in email with hyphens
#         trimmed_email = re.sub(r'[^a-z0-9-]', '-', trimmed_email)

#         # Generate a dynamic bucket name based on user ID and trimmed email
#         bucket_name = f'sign-{user_id}-{trimmed_email}'
#         # Ensure the bucket name is valid and within length constraints
#         if len(bucket_name) > 63:
#             bucket_name = bucket_name[:63]

#         s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#                           aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
#                           region_name=settings.AWS_REGION)

#         try:
#             if not bucket_exists(s3, bucket_name):
#                 s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': settings.AWS_REGION})
#                 return JsonResponse({'success': True, 'message': 'Bucket created successfully', 'bucket_name': bucket_name})
#             else:
#                 return JsonResponse({'success': False, 'error': 'Bucket already exists'}, status=400)
#         except Exception as e:
#             return JsonResponse({'success': False, 'error': str(e)}, status=500)
#     else:
#         return JsonResponse({'error': 'Method not allowed'}, status=405)

# def bucket_exists(s3, bucket_name):
#     try:
#         s3.head_bucket(Bucket=bucket_name)
#         return True
#     except boto3.exceptions.botocore.client.ClientError as e:
#         error_code = int(e.response['Error']['Code'])
#         if error_code == 404:
#             return False
#         else:
#             raise
# @csrf_exempt
# def upload_file_to_existing_bucket(request):
#     if request.method == 'POST':
#         file_object = request.FILES.get('file')
#         bucket_name = request.POST.get('bucket_name')

#         if not file_object or not bucket_name:
#             return JsonResponse({'success': False, 'error': 'File or bucket name not provided'}, status=400)

#         # Create an S3 client
#         s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#                           aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
#                           region_name=settings.AWS_REGION)

#         try:
#             # Upload file to the existing bucket
#             s3.upload_fileobj(file_object, bucket_name, file_object.name)
#             return JsonResponse({'success': True, 'message': 'File uploaded successfully'})
#         except Exception as e:
#             return JsonResponse({'success': False, 'error': str(e)}, status=500)
#     else:
#         return JsonResponse({'error': 'Method not allowed'}, status=405)

# ///// another api to check if bucket exists then add the file or make new bucket and then add the file
import re
import boto3
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def bucket_exists(s3, bucket_name):
    try:
        s3.head_bucket(Bucket=bucket_name)
        return True
    except boto3.exceptions.botocore.client.ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            return False
        else:
            raise

@csrf_exempt
def upload_file_to_s3(request):
    if request.method == 'POST':
        file_object = request.FILES.get('file')
        # user_id = request.POST.get('user_id')
        # user_email = request.POST.get('user_email')
        bucket_name = request.POST.get('bucket_name')

        if not file_object or not bucket_name:
            return JsonResponse({'success': False, 'error': 'File, user ID, user email, or bucket name not provided'}, status=400)

        s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                          region_name=settings.AWS_REGION)

        try:
            # Check if the bucket already exists
            if not bucket_exists(s3, bucket_name):
                # Create a new bucket
                s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': settings.AWS_REGION})

            # Upload file to the bucket
            s3.upload_fileobj(file_object, bucket_name, file_object.name)
            return JsonResponse({'success': True, 'message': 'File uploaded successfully', 'bucket_name': bucket_name})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


# /// fetch pdf from aws s3 bucket
import boto3
from botocore.exceptions import ClientError
from django.http import HttpResponse, JsonResponse
from django.conf import settings
 
# def fetch_pdf_from_s3(request, file_name):
#     bucket_name = 'bucketpdfdoc'
 
#     if not file_name or not bucket_name:
#         return JsonResponse({'success': False, 'error': 'File name or bucket name not provided'}, status=400)
 
#     # Create an S3 client
#     s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#                       aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
#                       region_name=settings.AWS_REGION)
 
#     try:
#         # Retrieve the PDF file object from S3 bucket
#         response = s3.get_object(Bucket=bucket_name, Key=file_name)
#         # Get the PDF file content from the response
#         pdf_content = response['Body'].read()
 
#         # Create an HTTP response with the PDF content
#         http_response = HttpResponse(pdf_content, content_type='application/pdf')
#         http_response['Content-Disposition'] = f'attachment; filename="{file_name}"'
#         return http_response
#     except ClientError as e:
#         return JsonResponse({'success': False, 'error': str(e)}, status=500)
 
@api_view(['GET'])
def fetch_pdf_from_s3(request, bucket_name, file_name):
    if not file_name or not bucket_name:
        return JsonResponse({'success': False, 'error': 'File name or bucket name not provided'}, status=400)

    # Create an S3 client
    s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                      region_name=settings.AWS_REGION)

    try:
        # Retrieve the PDF file object from S3 bucket
        response = s3.get_object(Bucket=bucket_name, Key=file_name)
        # Get the PDF file content from the response
        pdf_content = response['Body'].read()

        # Create an HTTP response with the PDF content
        return HttpResponse(pdf_content, content_type='application/pdf')
    except ClientError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

from rest_framework.decorators import api_view
# //// fetching s3_key based on docid
@api_view(['GET'])
def get_s3_key(request, docid):
    try:
        document = DocumentTable.objects.get(id=docid)
        s3_key = document.s3_key
        return Response({'s3_key': s3_key}, status=status.HTTP_200_OK)
    except DocumentTable.DoesNotExist:
        return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
 
 #////// download api from s3 -------Rajvi
@api_view(['GET'])
def generate_presigned_url(request, bucket_name, file_name):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )
    try:
        response = s3_client.generate_presigned_url('get_object',Params={'Bucket': bucket_name,'Key': file_name},          ExpiresIn=3600)
    except ClientError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': True, 'url': response})

@csrf_exempt
@api_view(['DELETE'])
def delete_file_from_s3(request):
    bucket_name = request.data.get('bucket_name')
    file_name = request.data.get('file_name')

    if not bucket_name or not file_name:
        return JsonResponse({'success': False, 'error': 'Bucket name or file name not provided'}, status=400)

    s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                      region_name=settings.AWS_REGION)

    try:
        s3.delete_object(Bucket=bucket_name, Key=file_name)
        return JsonResponse({'success': True, 'message': 'File deleted successfully'})
    except ClientError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
 
# ///// send email
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
            send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_emails)
            return JsonResponse({'success': True, 'message': 'Email sent successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)

# ===================================================================================
# celery
# ===================================================================================
# // perfectly working with sign button means if one user click on sign button it goes to 2nd then 2nd user click on sign button then goes to 3rd user like that with scheduling email of 2-4-6-8 as well ass one day before

from django.shortcuts import render
from .task import tasc_func
from django.http import HttpResponse
from send_mail_app.task import send_mail_func
from django_celery_beat.models import PeriodicTask,CrontabSchedule
import json
from django.utils import timezone
from django.utils.text import slugify
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime,timedelta
from send_mail_app.models import ScheduledEmail
from django.http import HttpResponse
from send_mail_app.models import EmailList
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import logging
import time
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from datetime import time
import logging
from django.shortcuts import redirect

logger = logging.getLogger(__name__)

def test(request):
    tasc_func.delay()
    return HttpResponse("Done")

def send_mail_to_all(request):
    send_mail_func.delay()
    return  HttpResponse("sent")

# @csrf_exempt
# def schedule_email(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body.decode('utf-8'))
#             recipient_email = data.get('email')
#             scheduled_date = data.get('scheduledDate')
#             reminder_days = data.get('reminderDays')  # Get the reminder days from the request data

#             scheduled_datetime = datetime.strptime(scheduled_date, '%Y-%m-%d')

#             # Calculate the reminder date for 4:00:00 PM
#             # remider before 24hrs
#             reminder_datetime_pm = scheduled_datetime - timedelta(days=1)
#             # remider interval
#             reminder_datetime_pm = reminder_datetime_pm.replace(hour=16, minute=0, second=0)

#             # Calculate the reminder date for 10:00:00 AM based on selected days
#             reminder_datetime_am = scheduled_datetime - timedelta(days=reminder_days)
#             reminder_datetime_am = reminder_datetime_am.replace(hour=14, minute=55, second=0)

#             expiration_days = (scheduled_datetime - datetime.now()).days

#             scheduled_email = ScheduledEmail.objects.create(
#                 recipient_email=recipient_email,
#                 scheduled_time=scheduled_datetime,
#                 expiration_days=expiration_days,
#                 reminder_date_pm=reminder_datetime_pm,
#                 reminder_date_am=reminder_datetime_am
#             )

#             # Create CrontabSchedules for both reminder times
#             crontab_schedule_pm, created_pm = CrontabSchedule.objects.get_or_create(
#                 minute=0,
#                 hour=16,
#                 day_of_month=reminder_datetime_pm.day,
#                 month_of_year=reminder_datetime_pm.month,
#                 defaults={'timezone': 'Asia/Kolkata'}
#             )

#             crontab_schedule_am, created_am = CrontabSchedule.objects.get_or_create(
#                 minute=55,
#                 hour=14,
#                 day_of_month=reminder_datetime_am.day,
#                 month_of_year=reminder_datetime_am.month,
#                 defaults={'timezone': 'Asia/Kolkata'}
#             )

#             # Create PeriodicTasks associated with the scheduled email and CrontabSchedules
#             task_name_pm = f"send_mail_to_{recipient_email.replace('@', '_').replace('.', '_')}_at_{reminder_datetime_pm.strftime('%Y_%m_%d_%H_%M')}_pm"
#             task_name_am = f"send_mail_to_{recipient_email.replace('@', '_').replace('.', '_')}_at_{reminder_datetime_am.strftime('%Y_%m_%d_%H_%M')}_am"

#             # Update or create PeriodicTasks for 4:00:00 PM reminder
#             PeriodicTask.objects.update_or_create(
#                 name=task_name_pm,
#                 defaults={
#                     'crontab': crontab_schedule_pm,
#                     'task': 'send_mail_app.task.send_mail_func',
#                     'args': json.dumps([scheduled_email.id]),
#                 }
#             )

#             # Update or create PeriodicTasks for 10:00:00 AM reminder
#             PeriodicTask.objects.update_or_create(
#                 name=task_name_am,
#                 defaults={
#                     'crontab': crontab_schedule_am,
#                     'task': 'send_mail_app.task.send_mail_func',
#                     'args': json.dumps([scheduled_email.id]),
#                 }
#             )

#             return JsonResponse({'message': 'Scheduled Email'}, status=200)
#         except json.JSONDecodeError:
#             return JsonResponse({'error': 'Invalid JSON format'}, status=400)
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
#     else:
#         return JsonResponse({'error': 'Invalid request method'}, status=400)
    
# # complete working to send the email through the approved button

# @csrf_exempt
# def send_emails(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             recipient_list = data.get('recipient_list', [])
#             if not recipient_list:
#                 return JsonResponse({"success": False, "message": "Recipient list is empty"}, status=400)

#             # Store email addresses in the database with status 'pending'
#             first_recipient_sent = False  # Flag to track if the first recipient has been sent the email
#             for recipient_email in recipient_list:
#                 email_obj = EmailList.objects.create(emails=recipient_email)
#                 # If the first recipient has not been sent the email yet, send it immediately
#                 if not first_recipient_sent:
#                     send_mail_to_recipient(email_obj)
#                     first_recipient_sent = True
#                 else:
#                     email_obj.save()  # Save the other recipients with status 'pending'

#             return JsonResponse({"success": True, "message": "Emails sent successfully"}, safe=False)
#         except Exception as e:
#             return JsonResponse({"success": False, "message": str(e)}, status=500)
#     else:
#         return JsonResponse({"success": False, "message": "Only POST requests are allowed"}, status=405)


# @csrf_exempt
# def email_approval(request, email_id):
#     if request.method == 'GET':
#         try:
#             email_obj = EmailList.objects.get(id=email_id)
#             if email_obj.status == 'sent':
#                 # Update the status of the current email to 'approved'
#                 email_obj.status = 'approved'
#                 email_obj.save()

#                 # Get the next pending email after the current email
#                 next_pending_email = EmailList.objects.filter(status='pending', id__gt=email_obj.id).first()

#                 # Send email to the next pending recipient if available
#                 if next_pending_email:
#                     send_mail_to_recipient(next_pending_email)

#                 # Redirect the user to the EmailList page
#                 return redirect('http://localhost:3000/EmailList')

#             else:
#                 return JsonResponse({"error": "Email has not been sent yet"}, status=400)
#         except EmailList.DoesNotExist:
#             return JsonResponse({"error": "Email not found"}, status=404)
#     else:
#         return JsonResponse({"error": "Invalid HTTP method"}, status=405)

# def send_mail_to_recipient(email_obj):
#     subject = "Test email from Django"
#     message = "Hello there!!\nSequential email from django."
#     message += "\n\nClick <a href='http://localhost:3000/EmailList'>here</a> to view the email list and approve."
#     from_email = settings.EMAIL_HOST_USER

#     send_mail(subject, message, from_email, [email_obj.emails], html_message=message)

#     # Update the status of the current email to 'sent'
#     email_obj.status = 'sent'
#     email_obj.save()


# fetching data for the UI 
def get_email_list(request):
    try:
        email_list = list(EmailList.objects.values('id', 'emails', 'status'))
        return JsonResponse({'email_list': email_list}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
from rest_framework.parsers import JSONParser

# save document withouth template 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

# Save the document record along with recipient detail
@csrf_exempt
def save_doc(request):
    try:
        if request.method == 'POST':
            data = JSONParser().parse(request)
            doc_name = data['name']
            userid = data['creator_id']

            user = User.objects.get(pk=userid)

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
            recipients = [
                DocumentRecipientDetail(
                    name=recipient_data['RecipientName'],
                    email=recipient_data['RecipientEmail'],
                    roleId=RecipientRole.objects.filter(
                        role_name = recipient_data["role"]
                    ).first(),
                    docId= document
                )
                for recipient_data in data['receipientData']
            ]
            DocumentRecipientDetail.objects.bulk_create(recipients)
            return JsonResponse({"doc_id":document.id,"message": "Document and recipients created successfully."})
        else:
            return JsonResponse({"error": "Invalid request method"}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


from django.http import JsonResponse
from .models import DocumentTable, DocumentRecipientDetail

@csrf_exempt
def get_doc(request):
    try:
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
def save_recipient_position_data(request):
    try:
        if request.method == 'POST':
            data = JSONParser().parse(request)
            newData1 = data["recipient_data"]
            
            Expiration = data["Expiration"]
            docId = data["docId"]
            s_send = data["s_send"]
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
            email_list = list(email_list)

            recipients = DocumentRecipientDetail.objects.filter(docId=docId)
            email_messages = []
            for rec in recipients:
                if rec.roleId_id == 1:
                    url = f"http://localhost:3000/#/recieverPanel?docType=doc&type=signer&did={docId}&rid={rec.id}"
                    message = doc.email_msg + f"\n\nFor signing click on below link : {url} \nIf you already done the signature ignore this remainder"
                elif rec.roleId_id == 2:
                    url = f"http://localhost:3000/#/recieverPanel?docType=doc&type=viewer&did={docId}&rid={rec.id}"
                    message = doc.email_msg + f"\n\nFor viewing pdf click on below link: {url}"
                else:
                    continue  

                email_messages.append({
                    'email': rec.email,
                    'subject': doc.email_title,
                    'message': message,
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
                sequence_emails(payload)
            elif doc.req_type == "C":
                sequence_emails(payload)
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

def none_send_email(email_messages,doc):
    try:
        for email_message in email_messages:
            recipient_email = email_message.get('email')
            subject = email_message.get('subject', '')
            message = email_message.get('message', '')
            try:
                email_obj = EmailList.objects.create(emails=recipient_email,status="sent", docId=doc)
                email_obj.save()
            finally:
                schedule_sequence_email({"email":recipient_email,"reminderDays":doc.reminderDays,"scheduledDate":doc.expirationDateTime,"doc_id":doc.id,"title":subject, "message":message})
                send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient_email])
        return JsonResponse({'success': True, 'message': 'Emails sent successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
    
def none_send_email_schedule(email_messages,doc,datetime):
    try:
        for email_message in email_messages:
            recipient_email = email_message.get('email')
            subject = email_message.get('subject', '')
            message = email_message.get('message', '')
            try:
                email_obj = EmailList.objects.create(emails=recipient_email,status="sent", docId=doc)
                email_obj.save()
            except Exception as e:
                print("Error creating or saving EmailList object:", e)
            finally:
                schedule_sequence_email({"email":recipient_email,"reminderDays":doc.reminderDays,"scheduledDate":doc.expirationDateTime,"doc_id":doc.id,"title":subject, "message":message})
                send_mail_to_sequence_recipient_schedule(recipient_email,subject,message,doc.id,datetime)
        return JsonResponse({'success': True, 'message': 'Emails sent successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
    


def send_mail_to_sequence_recipient(email_obj,subject,message,doc_id):
    # Update the status of the current email to 'sent'
    email_data = EmailList.objects.filter(docId=doc_id,emails=email_obj).first()
    email_data.status = 'sent'
    email_data.save()
    from_email = settings.EMAIL_HOST_USER
    send_mail(subject, message, from_email, [email_obj], html_message=message)

def send_mail_to_sequence_recipient_schedule(email_obj,subject,message,doc_id,scheduled_datetime):
    try:
        recipient_email = email_obj
        if isinstance(scheduled_datetime, str):
            scheduled_datetime = datetime.strptime(scheduled_datetime, '%d/%m/%Y, %H:%M')
            scheduled_datetime = timezone.make_aware(scheduled_datetime, timezone.get_current_timezone())
        
        if isinstance(scheduled_datetime, datetime):

            expiration_days = (scheduled_datetime - timezone.now()).days
            doc = DocumentTable.objects.get(pk=doc_id)

            scheduled_email = ScheduledEmail.objects.create(
                recipient_email=recipient_email,
                scheduled_time=scheduled_datetime,
                expiration_days=0,
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
                    'args': json.dumps([scheduled_email.id, subject, message]),
                }
            )
    except Exception as e:
        print("Error:", e)


def sequence_emails(data):
    try:
        recipient_list = data["recipient_list"]
        if not recipient_list:
            return JsonResponse({"success": False, "message": "Recipient list is empty"}, status=400)

        first_recipient_sent = False
        for recipient_email in recipient_list:
            doc_Id1 = DocumentTable.objects.filter(
                id = data["docID"]
            ).first()
            email_obj = EmailList.objects.create(emails=recipient_email['email'],docId=doc_Id1)
            if not first_recipient_sent:
                schedule_sequence_email({"email":recipient_email["email"],"reminderDays":data["rdays"],"scheduledDate":data['sdate'],"doc_id":data["docID"],"title":recipient_email['subject'], "message":recipient_email["message"]})
                if data["Schedule"]:
                    send_mail_to_sequence_recipient_schedule(recipient_email['email'],recipient_email['subject'],recipient_email["message"],data["docID"],data["scheduleDateAndTime"])
                else:
                    send_mail_to_sequence_recipient(recipient_email['email'],recipient_email['subject'],recipient_email["message"],data["docID"])
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
        doc = DocumentTable.objects.get(pk=doc_id)
        email_id = DocumentRecipientDetail.objects.filter(id=rid,docId=doc_id).first()
        if doc.req_type == "S":
            if email_id :
                email_obj =  EmailList.objects.filter(docId=doc_id,emails=email_id.email).first()
                if email_obj.status == 'sent':  
                    email_obj.status = 'approved'
                    email_obj.save()

                    next_pending_email = EmailList.objects.filter(status='pending', docId=doc_id).first()
                    if next_pending_email:
                        
                        recipients = DocumentRecipientDetail.objects.filter(docId=doc_id,email=next_pending_email.emails).first()
                        if recipients.roleId.role_id == 1:
                            url = f"http://localhost:3000/#/recieverPanel?docType=doc&type=signer&did={doc_id}&rid={recipients.id}"
                            message = doc.email_msg + f"\n\nFor signing click on below link : {url} \nIf you already done the signature ignore this remainder"
                        elif recipients.roleId.role_id == 2:
                            url = f"http://localhost:3000/#/recieverPanel?docType=doc&type=viewer&did={doc_id}&rid={recipients.id}"
                            message = doc.email_msg + f"\n\nFor viewing pdf click on below link: {url}"
                        schedule_sequence_email({"email":next_pending_email.emails,"reminderDays":doc.reminderDays,"scheduledDate":doc.expirationDateTime,"doc_id":doc_id,"title":doc.email_title, "message":message})
                        send_mail_to_sequence_recipient(next_pending_email.emails,doc.email_title,message,doc_id)
                        return JsonResponse({"success": True}, safe=False,status=200)
                    else:
                        doc = DocumentTable.objects.get(pk=doc_id)
                        doc.status = "Completed"
                        doc.save()
                        return JsonResponse({"error": "Email already has been sent..!!"}, status=400)
                else:
                    return JsonResponse({"error": "No more user to send..!!"}, status=400)
            else:
                    return JsonResponse({"error": "Recipient data not found..!!"}, status=404)
        elif doc.req_type == "N":
            if email_id :
                email_obj =  EmailList.objects.filter(docId=doc_id)
                for data in email_obj: 
                    if data.emails==email_id.email:
                        if data.status == 'sent':  
                            # Update the status of the current email to 'approved'
                            data.status = 'approved'
                            data.save()
                
                email_obj =  EmailList.objects.filter(docId=doc_id)
                all_approved = True  # Assume all emails are approved initially

                for data in email_obj:
                    if data.status != 'approved':
                        all_approved = False  # If any email is not approved, set flag to False
                        break  # No need to continue checking, as we already found a non-approved email

                if all_approved:
                    doc = DocumentTable.objects.get(pk=doc_id)
                    doc.status = "Completed"
                    doc.save()
                    return JsonResponse({"Success": "Document complete!!"}, status=200)
                return JsonResponse({"success": True}, safe=False,status=200)
            else:
                return JsonResponse({"error": "Recipient data not found..!!"}, status=404)
        elif doc.req_type == "C":
            if email_id :
                email_obj =  EmailList.objects.filter(docId=doc_id,emails=email_id.email).first()
                if email_obj.status == 'sent':  
                    email_obj.status = 'approved'
                    email_obj.save()
                    next_pending_email = EmailList.objects.filter(status='pending', docId=doc_id)
                    
                    for data in next_pending_email:

                        recipients = DocumentRecipientDetail.objects.filter(docId=doc_id, email=data.emails).first()
                        if not recipients:
                            continue

                        if recipients.roleId.role_id == 1:
                            url = f"http://localhost:3000/#/recieverPanel?docType=doc&type=signer&did={doc_id}&rid={recipients.id}"
                            message = doc.email_msg + f"\n\nFor signing click on below link: {url} \nIf you already done the signature ignore this remainder"
                        elif recipients.roleId.role_id == 2:
                            url = f"http://localhost:3000/#/recieverPanel?docType=doc&type=viewer&did={doc_id}&rid={recipients.id}"
                            message = doc.email_msg + f"\n\nFor viewing pdf click on below link: {url} \nIf you already done the signature ignore this remainder"
                        else:
                            continue

                        schedule_sequence_email({"email":data.emails,"reminderDays":doc.reminderDays,"scheduledDate":doc.expirationDateTime,"doc_id":doc_id,"title":doc.email_title, "message":message})
                        send_mail_to_sequence_recipient(data.emails, doc.email_title, message, doc_id)
                    
                    email_obj = EmailList.objects.filter(docId=doc_id)
                    all_approved = True

                    for data in email_obj:
                        if data.status != 'approved':
                            all_approved = False
                            break  

                    if all_approved:
                        doc = DocumentTable.objects.get(pk=doc_id)
                        doc.status = "Completed"
                        doc.save()
                        return JsonResponse({"Success": "Document complete!!"}, status=200)
                    return JsonResponse({"success": "Emails sent successfully."}, status=200)
                else:
                    return JsonResponse({"error": "No more user to send..!!"}, status=400)
            else:
                    return JsonResponse({"error": "Recipient data not found..!!"}, status=404)
        else:
            return JsonResponse({"error": "No method of req_type found ..!!"}, status=404)
    except EmailList.DoesNotExist:
        return JsonResponse({"error": "Email not found"}, status=404)

def schedule_sequence_email(data):
    try:
        print("==================1===========================")
        recipient_email = data['email']
        scheduled_date = data['scheduledDate']
        print("scheduled_date : ",type(scheduled_date))
        reminder_days = data['reminderDays']
        doc_id = data['doc_id']
        message = data['message']
        title = data['title']
        print("====================2=========================")
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
        print("Formatted scheduled_date:", formatted_date)

        # scheduled = datetime.strptime(scheduled_date, '%Y-%m-%d %H:%M:%S%z')
        # print("+++++++++++++++++++",scheduled)
        # # Format the datetime object as per the required format
        # formatted_date = scheduled.strftime('%d-%m-%Y')
        # scheduled_date = type(scheduled_date)

        # Parse the string to a datetime object
       
        scheduled_datetime = timezone.make_aware(datetime.strptime(formatted_date,'%d-%m-%Y'), timezone.get_current_timezone())
        print("===================3==========================")
        # Calculate the reminder date for 4:00:00 PM
        reminder_datetime_pm = scheduled_datetime - timedelta(days=1)
        reminder_datetime_pm = reminder_datetime_pm.replace(hour=16, minute=0, second=0)
        print("===================4==========================")
        # Calculate the reminder date for 10:00:00 AM based on selected days
        reminder_datetime_am = scheduled_datetime - timedelta(days=reminder_days)
        reminder_datetime_am = reminder_datetime_am.replace(hour=16, minute=40, second=0)
        print("===================5==========================")
        expiration_days = (scheduled_datetime - timezone.now()).days
        doc = DocumentTable.objects.get(pk=doc_id)
        print("===================6==========================") 
        print(doc)
        scheduled_email = ScheduledEmail.objects.create(
            recipient_email=recipient_email,
            scheduled_time=scheduled_datetime,
            expiration_days=expiration_days,
            reminder_date_pm=reminder_datetime_pm,
            reminder_date_am=reminder_datetime_am,
            doc_id=doc
        )
        print("==================***********************************************==")
        # Create CrontabSchedules for both reminder times
        crontab_schedule_pm, created_pm = CrontabSchedule.objects.get_or_create(
            minute=0,
            hour=16,
            day_of_month=reminder_datetime_pm.day,
            month_of_year=reminder_datetime_pm.month,
            defaults={'timezone': 'Asia/Kolkata'}
        )

        crontab_schedule_am, created_am = CrontabSchedule.objects.get_or_create(
            minute=40,
            hour=16,
            day_of_month=reminder_datetime_am.day,
            month_of_year=reminder_datetime_am.month,
            defaults={'timezone': 'Asia/Kolkata'}
        )
        print("==================***********************************************==")
        # Create PeriodicTasks associated with the scheduled email and CrontabSchedules
        task_name_pm = f"send_mail_to_{recipient_email.replace('@', '_').replace('.', '_')}_at_{reminder_datetime_pm.strftime('%Y_%m_%d_%H_%M')}_pm"
        task_name_am = f"send_mail_to_{recipient_email.replace('@', '_').replace('.', '_')}_at_{reminder_datetime_am.strftime('%Y_%m_%d_%H_%M')}_am"
        print("==================***********************************************==")
        # Update or create PeriodicTasks for 4:00:00 PM reminder
        PeriodicTask.objects.update_or_create(
            name=task_name_pm,
            defaults={
                'crontab': crontab_schedule_pm,
                'task': 'send_mail_app.task.send_mail_func',
                'args': json.dumps([scheduled_email.id,title,message]),
            }
        )
    
        # Update or create PeriodicTasks for 10:00:00 AM reminder
        PeriodicTask.objects.update_or_create(
            name=task_name_am,
            defaults={
                'crontab': crontab_schedule_am,
                'task': 'send_mail_app.task.send_mail_func',
                'args': json.dumps([scheduled_email.id,title,message]),
            }
        )

        return JsonResponse({'message': 'Scheduled Email'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
class CurrentUserView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


    def get(self, request):
        serializer = UserSerializer(request.user)
        print("=====================================",serializer)
        return Response(serializer.data)
    
class DocAllRecipientById(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, Doc_id):
        try:
            # Retrieve TemplateDraggedData objects based on the provided template_id
            rec_data = DocumentRecipientDetail.objects.filter(docId=Doc_id)
            serializer = DocumentRecipientSerializer(rec_data, many=True)
            return JsonResponse(serializer.data,safe=False)
        except DocumentRecipientDetail.DoesNotExist:
            return Response({"error": "Template Recipient Data not found for the given template_id"}, status=status.HTTP_404_NOT_FOUND)
 
class GetDraggedDataByDocRec(APIView):
    def get(self, request, docId,docRecipientdetails_id):
        recipient_positions = RecipientPositionData.objects.filter(docId=docId, docRecipientdetails_id=docRecipientdetails_id)
        serializer = DocumentPositionSerializer(recipient_positions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# Home page changes 
# class DocumentView2(APIView):
#     def post(self, request, format=None):
#         created_by_you = request.data.get('createdByYou')
#         created_by_others = request.data.get('createdByOthers')
#         user_id = request.data.get('userid')

#         if created_by_you and created_by_others:
#             documents = DocumentTable.objects.select_related('creator_id').select_related('last_modified_by').all()
#         elif created_by_you:
#             documents = DocumentTable.objects.filter(creator_id=user_id).select_related('creator_id').select_related('last_modified_by').all()
#         else:
#             documents = DocumentTable.objects.exclude(creator_id=user_id).select_related('creator_id').select_related('last_modified_by').all()

#         serializer = DocumentSerializer(documents, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

class DocumentView2(APIView):
    def post(self, request, format=None):
        created_by_you = request.data.get('createdByYou')
        created_by_others = request.data.get('createdByOthers')
        user_id = request.data.get('userid')
        email = User.objects.get(id=user_id).email

        if not user_id:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        if created_by_you and created_by_others:
            documents = DocumentTable.objects.filter(
                Q(creator_id=user_id) |
                Q(id__in=DocumentRecipientDetail.objects.filter(email=email).values_list('docId', flat=True))
            ).select_related('creator_id', 'last_modified_by')
        elif created_by_you:
            documents = DocumentTable.objects.filter(creator_id=user_id).select_related('creator_id', 'last_modified_by')
        elif created_by_others:
            documents = DocumentTable.objects.filter(
                Q(id__in=DocumentRecipientDetail.objects.filter(email=email).values_list('docId', flat=True)) &
                ~Q(creator_id=user_id)
            ).select_related('creator_id', 'last_modified_by')
        else:
            return Response({"error": "Invalid request parameters"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# /// sakshi views
@csrf_exempt
def save_multiple_doc(request):
    try:
        if request.method == 'POST':
            data = JSONParser().parse(request)
            print(data)
            if 'name' not in data:
                return JsonResponse({'error': 'Missing field: name'}, status=400)
            doc_name = data['name']
            userid = data['creator_id']

            user = User.objects.get(pk=userid)

            existing_template = BulkPdfDocumentTable.objects.filter(
                name=doc_name, creator_id=user
            ).exists()

            if existing_template:
                return JsonResponse(
                    {"error": "Document with the same name already exists for this user."},
                    status=400
                )

            # Create the document
            document = BulkPdfDocumentTable.objects.create(
                name=data['name'],
                selectedPdfs=data['selectedPdfs'],
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
            print("name: ",data['name'])
            print(data['receipientData'])
            recipients = [
                BulkPdfRecipientDetail(
                    name=recipient_data['RecipientName'],
                    email=recipient_data['RecipientEmail'],
                    roleId=RecipientRole.objects.filter(
                        role_name = recipient_data['role']
                    ).first(),
                    docId= document
                )
                for recipient_data in data['receipientData']
            ]
            BulkPdfRecipientDetail.objects.bulk_create(recipients)
            return JsonResponse({"doc_id":document.id,"message": "Document and recipients created successfully."})
        else:
            return JsonResponse({"error": "Invalid request method"}, status=405)
    except Exception as e:
        print('error:', str(e))
        return JsonResponse({'error': str(e)}, status=400)

class getRecipientCount(APIView):
    def post(self, request):
        doc_id = request.data.get('docid')
        if not doc_id:
            return Response({"error": "Document ID not provided"}, status=status.HTTP_400_BAD_REQUEST)
        count = DocumentRecipientDetail.objects.filter(docId=doc_id).count()
        pending_count = RecipientPositionData.objects.filter(
            Q(docId=doc_id) &
            (Q(reviewer_status='pending') | Q(reviewer_status='sent') | Q(signer_status='pending') | Q(signer_status='sent'))
        ).distinct().count()
        # pendingCount = RecipientPositionData.objects.filter(docId=doc_id).filter(reviewer_status='Pending' or reviewer_status='sent' or signer_status='Pending' or signer_status='sent').count().distinct()
        return Response({"recipient_count": count, "pending_count":pending_count, "docId":doc_id}, status=status.HTTP_200_OK)
 
class getRecipientDetails(APIView):
    def post(self, request, format=None):
        doc_id = request.data.get('docid')
       
        if not doc_id:
            return Response({"error": "Document ID is required"}, status=status.HTTP_400_BAD_REQUEST)
 
        # Querysets for documents created by the user and documents where the user is a recipient
        recipients = DocumentRecipientDetail.objects.filter(docId=doc_id)
 
        serializer = DocumentRecipientSerializer(recipients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
   
class getStatus(APIView):
    def post(self, request, format=None):
        doc_id = request.data.get('docid')
        email = request.data.get('email')
        if not doc_id and not email:
            return Response({"error": "Document ID and Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not doc_id:
            return Response({"error": "Document ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not email:
            return Response({"error": "Document ID and Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        # Querysets for documents created by the user and documents where the user is a recipient
        data = EmailList.objects.filter(docId=doc_id).filter(emails=email)
 
        serializer = EmailListSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
 
class getPendingRecipientCount(APIView):
    def post(self, request):
        doc_id = request.data.get('docid')
        if not doc_id:
            return Response({"error": "Document ID not provided"}, status=status.HTTP_400_BAD_REQUEST)
        pending_count = EmailList.objects.filter(
            Q(docId=doc_id) &
            (Q(status='pending') | Q(status='sent') | Q(status='Pending') | Q(status='Sent'))
        ).distinct().count()
        # pendingCount = RecipientPositionData.objects.filter(docId=doc_id).filter(reviewer_status='Pending' or reviewer_status='sent' or signer_status='Pending' or signer_status='sent').count().distinct()
        return Response({"pending_count":pending_count}, status=status.HTTP_200_OK)

class deleteDocumentView(APIView):
    def post(self, request):
        # Assuming 'docid' is passed in the request data
        doc_id = request.data.get('docid')
        if not doc_id:
            return Response({"error": "Document ID not provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Get the document object
        document = get_object_or_404(DocumentTable, id=doc_id)

        # Delete the document
        document.delete()

        # Optionally, you can return details of the deleted document or a success message
        return Response({"message": "Document deleted successfully","status":200}, status=status.HTTP_200_OK)
    
import requests
import base64
@csrf_exempt
@require_POST
def googleLogIn(request):
    data = JSONParser().parse(request)
    print(data['token'])
    access_token = data['token']
    url = f'https://www.googleapis.com/oauth2/v1/userinfo?access_token={access_token}'

    try:
        # Make the GET request to Google API
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            user_info = response.json()
            print(user_info)
            profile_pic = user_info.get("picture", "")

            # Fetch and convert profile picture to binary string if it exists
            if profile_pic:
                image_response = requests.get(profile_pic)
                if image_response.status_code == 200:
                    binary_string = base64.b64encode(image_response.content).decode('utf-8')
                else:
                    binary_string = ""
            else:
                binary_string = ""

            res = User.objects.filter(email=user_info['email']).first()
            if not res:
                res = User.objects.create(
                    email=user_info['email'],
                    password="",
                    full_name=user_info["name"],
                    signIn_with_google="Y",
                    profile_pic=binary_string 
                )
                
                signature_data = {
                    'draw_img_name': None, 
                    'draw_enc_key': None,
                    'img_name': None,
                    'img_enc_key': None,
                    'user_id_id': res.id,
                }
                initial_data = {
                    'draw_img_name': None, 
                    'draw_enc_key': None,
                    'img_name': None,
                    'img_enc_key': None,
                    'user_id_id': res.id,
                }

                Signature.objects.create(**signature_data)
                Initials.objects.create(**initial_data)
                
            print(res.id)
            payload = {
                'id': res.id,
                'exp': datetime.utcnow() + timedelta(hours=24),  # Use datetime.utcnow() for JWT standard
                'iat': datetime.utcnow()
            }
            token = jwt.encode(payload, 'secret', algorithm='HS256')
    
            # response2 = Response()
            # response2.set_cookie(key='jwt', value=token, httponly=True)
            resData = {'jwt': token}
            return JsonResponse(resData)
        else:
            # Handle errors
            return JsonResponse({'error': 'Failed to retrieve user info'}, status=response.status_code)
    except requests.exceptions.RequestException as e:
        # Handle request exception
        print(e)
        return JsonResponse({'error': str(e)}, status=500)

class EmailListAPIView(APIView):
    def get(self, request, docId, recEmail):
        email_list = EmailList.objects.filter(docId=docId, emails=recEmail)
        serializer = EmailListSerializer(email_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class DocumentRecipientDetailAPIView(APIView):
    def get(self, request, docId, recEmail):
        recipient_details = DocumentRecipientDetail.objects.filter(docId=docId, email=recEmail)
        print("recipient_details", recipient_details)
        serializer = DocumentRecipientSerializer(recipient_details, many=True)
        print("abcd recipientdetails", serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

from send_mail_app.task import delete_expired_documents
@csrf_exempt
def trigger_delete_expired_documents(request):
    if request.method == 'POST':
        delete_expired_documents.delay()  # Trigger the Celery task asynchronously
        return JsonResponse({'message': 'Task to delete expired documents has been triggered.'})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


class FetchRecipientFullDetails(APIView):
    def get(self, request, recipient_id):
        try:
            recipient_detail = DocumentRecipientDetail.objects.get(pk=recipient_id)
            serializer = DocumentRecipientSerializer(recipient_detail)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except DocumentRecipientDetail.DoesNotExist:
            return Response({"error": "Recipient not found"}, status=status.HTTP_404_NOT_FOUND)