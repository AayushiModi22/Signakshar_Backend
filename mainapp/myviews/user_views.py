from django.shortcuts import redirect, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import IsAuthenticated
from mainapp.serializers import *
from mainapp.models import *
import jwt
from datetime import datetime, timedelta
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import JsonResponse
from rest_framework import status
from django.forms import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import requests
import base64
from rest_framework.parsers import JSONParser
from rest_framework.parsers import MultiPartParser, FormParser
from social_django.utils import psa
from ..decorators.logging import log_api_request 
from django.utils.decorators import method_decorator

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
    # @method_decorator(log_api_request)
    # def dispatch(self, request, *args, **kwargs):
    #     return super().dispatch(request, *args, **kwargs)

    # def post(self, request):
    #     print("user_views Registerview")
    #     serializer = UserSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     new_user = serializer.save()
    #     uid = new_user.id

    #     try:
    #         data = request.data
    #         signature_data = {
    #             # 'id': uid,
    #             'draw_img_name': data.get('draw_img_name_signature'),
    #             'draw_enc_key': data.get('draw_enc_key'),
    #             'img_name': data.get('img_name_signature'),
    #             'img_enc_key': data.get('img_enc_key'),
    #             'user_id_id': new_user.id,
    #             'sign_text_color' : data.get('sign_text_color'),
    #             'sign_text_font' : data.get('sign_text_font'),
    #             'sign_text_value' : data.get('sign_text_value'),
    #             'sign_text': data.get('signature_text'),
    #         }

    #         initial_data = {
    #             # 'id': new_user.id,
    #             'draw_img_name': data.get('draw_img_name_initials'),
    #             'draw_enc_key': data.get('draw_enc_key'),
    #             'img_name': data.get('img_name_initials'),
    #             'img_enc_key': data.get('img_enc_key'),
    #             'user_id_id': new_user.id,
    #             'initial_text_color' : data.get('initial_text_color'),
    #             'initial_text_font' : data.get('initial_text_font'),
    #             'initial_text_value' : data.get('initial_text_value'),
    #             'initial_text': data.get('initial_text'),
    #         }
    #         signatureTableData = Signature.objects.create(**signature_data)
    #         initialTableData = Initials.objects.create(**initial_data)
    #     except KeyError as e:
    #         return JsonResponse({'error': str(e)}, status=400)
    #     return Response(serializer.data)
    @method_decorator(log_api_request)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        print("user_views Registerview")
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_user = serializer.save()

        # Generate JWT token after successful registration
        payload = {
            'id': new_user.id,
            'exp': datetime.utcnow() + timedelta(days=1),  # Token valid for 1 day
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, 'secret', algorithm='HS256')

        # Print the token to the console
        print(f"JWT Token: {token}")

        # Return the token along with the user data
        return Response({
            'user': serializer.data,
            'jwt': token
        })

# @log_api_request
class LoginView(APIView):
    @method_decorator(log_api_request)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        email = request.data['email']
        password = request.data['password']
 
        user = User.objects.filter(email=email).first()
 
        if user is None:
            raise AuthenticationFailed('User not found!')
        if user.signIn_with_google=="Y":
            raise AuthenticationFailed('You have logged in with google!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')
       
        payload = {
            'id': user.id,
            'exp': datetime.utcnow() + timedelta(days=1),  # Use datetime.utcnow() for JWT standard
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, 'secret', algorithm='HS256')
 
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {'jwt': token}
        return response


@csrf_exempt
@require_POST
@log_api_request
def googleLogIn(request):
    data = JSONParser().parse(request)
    access_token = data['token']
    url = f'https://www.googleapis.com/oauth2/v1/userinfo?access_token={access_token}'

    try:
        response = requests.get(url)
        if response.status_code == 200:
            user_info = response.json()
            profile_pic = user_info.get("picture", "")
            if profile_pic:
                image_response = requests.get(profile_pic)
                print(image_response)
                if image_response.status_code == 200:
                    binary_string = "data:image/png;base64,"+base64.b64encode(image_response.content).decode('utf-8')
                    print(binary_string)
                else:
                    binary_string = ""
            else:
                binary_string = ""

            res = User.objects.filter(email=user_info['email']).first()
            print(binary_string)
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
                    'sign_text_color' : None,
                    'sign_text_font' : None,
                    'sign_text_value' : None,
                    'sign_text' : "sign text url",
                }
                initial_data = {
                    'draw_img_name': None, 
                    'draw_enc_key': None,
                    'img_name': None,
                    'img_enc_key': None,
                    'user_id_id': res.id,
                    'initial_text_color' : None,
                    'initial_text_font' : None,
                    'initial_text_value' : None,
                    'initial_text' : None,
                }

                Signature.objects.create(**signature_data)
                Initials.objects.create(**initial_data)
            payload = {
                'id': res.id,
                'exp': datetime.utcnow() + timedelta(days=1),  # Use datetime.utcnow() for JWT standard
                'iat': datetime.utcnow()
            }
            token = jwt.encode(payload, 'secret', algorithm='HS256')
            resData = {'jwt': token}
            return JsonResponse(resData)
        else:
            # Handle errors
            return JsonResponse({'error': 'Failed to retrieve user info'}, status=response.status_code)
    except requests.exceptions.RequestException as e:
        # Handle request exception
        print(e)
        return JsonResponse({'error': str(e)}, status=500)
     
     
class logoutview(APIView):
    @method_decorator(log_api_request)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {'message': 'success'}
        return response
 
class UserView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
 
    def get(self, request):
        print("user_views UserView")
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
 
class UserUpdateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    
    @method_decorator(log_api_request)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def put(self, request):
        print("user_views UserUpdateView")
        user = request.user
        
        user_data = {
            'full_name': request.data.get('user[full_name]'),
            'initial': request.data.get('user[initial]'),
            'profile_pic': request.data.get('user[profile_pic]'),
            'stamp_img_name':request.data.get('user[stamp_img_name]')
        }
        signature_data = {
            'draw_img_name': request.data.get('signature[draw_img_name]'),
            'draw_enc_key': request.data.get('signature[draw_enc_key]'),
            'img_name': request.data.get('signature[img_name]'),
            'img_enc_key': request.data.get('signature[img_enc_key]'),
            'sign_text_color': request.data.get('signature[sign_text_color]'),
            'sign_text_font': request.data.get('signature[sign_text_font]'),
            'sign_text_value': request.data.get('signature[sign_text_value]'),
            'sign_text': request.data.get('signature[signature_text]'),
        }
        initials_data = {
            'draw_img_name': request.data.get('initials[draw_img_name]'),
            'draw_enc_key': request.data.get('initials[draw_enc_key]'),
            'img_name': request.data.get('initials[img_name]'),
            'img_enc_key': request.data.get('initials[img_enc_key]'),
            'initial_text_color': request.data.get('signature[initial_text_color]'),
            'initial_text_font': request.data.get('signature[initial_text_font]'),
            'initial_text_value': request.data.get('signature[initial_text_value]'),
            'initial_text': request.data.get('signature[initial_text]'),
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
    def get(self, request, user_id):
        print("user_views FetchUserDetailsView")
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

class CurrentUserView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

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

class CheckEmailView(APIView):
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            return Response({'exists': True}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'exists': False}, status=status.HTTP_200_OK) 