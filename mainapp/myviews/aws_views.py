import boto3
from django.http import JsonResponse
import boto3
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import HttpResponse
from rest_framework.response import Response 
from rest_framework import status
from rest_framework.decorators import api_view
from mainapp.models import DocumentTable

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


import boto3
from botocore.exceptions import ClientError
from django.http import HttpResponse, JsonResponse
from django.conf import settings
 
@api_view(['GET'])
def fetch_pdf_from_s3(request, bucket_name, file_name):
    if not file_name or not bucket_name:
        return JsonResponse({'success': False, 'error': 'File name or bucket name not provided'}, status=400)

    # Create an S3 client
    s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                      region_name=settings.AWS_REGION)

    try:
        print("aws_views fetch pdf")
        # Retrieve the PDF file object from S3 bucket
        response = s3.get_object(Bucket=bucket_name, Key=file_name)
        # Get the PDF file content from the response
        pdf_content = response['Body'].read()

        # Create an HTTP response with the PDF content
        return HttpResponse(pdf_content, content_type='application/pdf')
    except ClientError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

from rest_framework.decorators import api_view

@api_view(['GET'])
def get_s3_key(request, docid):
    try:
        document = DocumentTable.objects.get(id=docid)
        s3_key = document.s3_key
        return Response({'s3_key': s3_key}, status=status.HTTP_200_OK)
    except DocumentTable.DoesNotExist:
        return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
 

@api_view(['GET'])
def generate_presigned_url(request, bucket_name, file_name):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )
    try:
        print("aws_views generate_presigned_url")
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
 