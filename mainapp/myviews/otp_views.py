from django.conf import settings
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from rest_framework.decorators import api_view
from django.utils import timezone

from mainapp.models import User, otpUser
from rest_framework.response import Response  
from django.views.decorators.http import require_POST
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import random
import string


def send_emailnew(recipient, subject, message):
    try:
        send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient])
        return True
    except Exception as e:
        return False


def send_email_with_otp(recipient_email, otp, username):
    # Render the HTML content using the template
    # html_content = render_to_string('otp-template/otp-template.html', {'otp': otp})
    html_content = render_to_string(
        'otp-template/otp-template.html', {'otp': otp, 'username': username})
    text_content = strip_tags(html_content)

    # Create the email
    email = EmailMultiAlternatives(
        subject='Your OTP Code',
        body=text_content,
        from_email=settings.EMAIL_HOST_USER,
        to=[recipient_email]
    )
    email.attach_alternative(html_content, "text/html")

    # Send the email
    email.send()


@csrf_exempt
@api_view(["POST"])
def sendOtp(request):
    print("otp_views sendOtp")
    body_data = request.data
    new_OTP = generate_otp()
    try:
        if not body_data["email"]:
            return Response({
                'Status': 400,
                'StatusMsg': "Email is required..!!"
            })

        emailExistInComapny = User.objects.filter(email=body_data["email"])

        if not filter:
            if (emailExistInComapny):
                return Response({
                    'Status': 400,
                    'StatusMsg': "This email already register..!!"
                })

        if filter == "F":
            if not emailExistInComapny:
                return Response({
                    'Status': 400,
                    'StatusMsg': "User not register..!!"
                })

        try:
            OTPEntry = otpUser.objects.get(email=body_data["email"])
            OTPEntry.otp = new_OTP
            OTPEntry.status = "N"
            OTPEntry.entry_date = timezone.now()
            OTPEntry.save()
        except otpUser.DoesNotExist:
            OTPEntry = otpUser.objects.create(
                email=body_data["email"], otp=new_OTP, status="N")
    except Exception as e:
        return Response({
            'Status': 400,
            'StatusMsg': "Error while sending OTP: " + str(e)
        })

    if OTPEntry:
        try:
            username = body_data["email"].split("@")[0]
            send_email_with_otp(body_data["email"], new_OTP, username)
            return Response({
                'Status': 200,
                'StatusMsg': "OTP sent successfully..!!"
            })
        except Exception as e:
            return Response({
                'Status': 500,
                'StatusMsg': "Error while sending OTP email: " + str(e)
            })

    return Response({
        'Status': 400,
        'StatusMsg': "Error while sending OTP..!!"
    })


def generate_otp():
    otp = ''.join(random.choices(string.digits, k=6))
    return otp


@csrf_exempt
@api_view(["POST"])
def verifyOtp(request):
    print("otp_views verifyOtp")
    body_data = request.data

    try:
        if not body_data["email"]:
            return Response({
                'Status': 400,
                'StatusMsg': "Email is required..!!"
            })
        if not body_data["otp"]:
            return Response({
                'Status': 400,
                'StatusMsg': "OTP is required..!!"
            })

        OTPEntry = otpUser.objects.get(
            email=body_data["email"], otp=body_data["otp"])

        if (OTPEntry.status == "Y"):
            return Response({
                'Status': 200,
                'StatusMsg': "OTP already veryfied..!!"
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
            'Status': 200,
            'StatusMsg': "OTP veryfied..!!"
        })
    except otpUser.DoesNotExist:
        return Response({
            'Status': 400,
            'StatusMsg': "Invalid Email or OTP ..!!"
        })


@csrf_exempt
@require_POST
def forgetPassword(request):
    print("otp_views forgetPassword")
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
