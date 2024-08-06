from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

@api_view(['POST'])
def send_test_email(request):
    try:
        send_mail(
            "hello",
            "Hey how are you..!!",
            'signakshar74@gmail.com',  # Replace with your email
            ['maayushi2003@gmail.com']
        )
        return Response({'message': 'Email sent successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)  # Print the error for debugging
        return Response({'error': f'Error sending email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
