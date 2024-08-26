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
from ..decorators.logging import log_api_request  # Import your decorator
from mainapp.models import DocumentTable
import boto3
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import io
import base64
import fitz 

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
@log_api_request
def upload_file_to_s3(request):
    if request.method == 'POST':
        file_object = request.FILES.get('file')
        bucket_name = request.POST.get('bucket_name')
        if not file_object or not bucket_name:
            return JsonResponse({'success': False, 'error': 'File or bucket name not provided'}, status=400)

        s3 = boto3.client('s3', 
                          aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                          region_name=settings.AWS_REGION)

        try:
            if not bucket_exists(s3, bucket_name):
                s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': settings.AWS_REGION})

            s3.upload_fileobj(file_object, bucket_name, file_object.name)
            return JsonResponse({'success': True, 'message': 'File uploaded successfully', 'bucket_name': bucket_name})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

def prefix_exists(s3, bucket_name, prefix):
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix, MaxKeys=1)
    return 'Contents' in response


@csrf_exempt
@log_api_request
def upload_template_file_to_s3(request):
    if request.method == 'POST':
        file_object = request.FILES.get('file')
        bucket_name = request.POST.get('bucket_name')
        template_bucket_name = request.POST.get('template_bucket_name')

        if not file_object or not bucket_name or not template_bucket_name:
            return JsonResponse({'success': False, 'error': 'File, bucket name, or template bucket name not provided'}, status=400)

        s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                          region_name=settings.AWS_REGION)

        try:
            # Check if the main bucket exists, if not create it
            if not bucket_exists(s3, bucket_name):
                s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': settings.AWS_REGION})

            # Check if the nested "bucket" (actually a prefix) exists
            nested_prefix = f"{template_bucket_name}/"
            if not prefix_exists(s3, bucket_name, nested_prefix):
                # Create a "folder" in S3 (S3 has a flat structure, but you can simulate folders using zero-byte objects with a trailing slash)
                s3.put_object(Bucket=bucket_name, Key=nested_prefix)

            # Upload the file to the nested bucket
            print("---upload_template_file_to_s3",nested_prefix)
            s3.upload_fileobj(file_object, bucket_name, f"{nested_prefix}{file_object.name}")

            return JsonResponse({'success': True, 'message': 'File uploaded successfully', 'bucket_name': bucket_name, 'nested_bucket': nested_prefix})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

# @csrf_exempt
# @log_api_request
# def fetch_templateFile_from_s3(request,bucket_name,template_bucket_name,file_name):
#     if request.method == 'GET':
#         if not bucket_name or not template_bucket_name or not file_name:
#             return JsonResponse({'success': False, 'error': 'Bucket name, template bucket name, or PDF name not provided'}, status=400)

#         s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#                           aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
#                           region_name=settings.AWS_REGION)

#         try:
#             # Check if the nested "bucket" (prefix) exists
#             nested_prefix = f"{template_bucket_name}/{file_name}"
#             if prefix_exists(s3, bucket_name, nested_prefix):
#                 # Fetch the PDF file from S3
#                 response = s3.get_object(Bucket=bucket_name, Key=nested_prefix)
#                 pdf_data = response['Body'].read()

#                 # Return the PDF data as a response
#                 return HttpResponse(pdf_data, content_type='application/pdf')
#             else:
#                 return JsonResponse({'success': False, 'error': f'PDF file {file_name} not found in template bucket {template_bucket_name}'}, status=404)
#         except Exception as e:
#             return JsonResponse({'success': False, 'error': str(e)}, status=500)
#     else:
#         return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
@log_api_request
def fetch_templateFile_from_s3(request, bucket_name, template_bucket_name, file_name):
    if request.method == 'GET':
        if not bucket_name or not template_bucket_name or not file_name:
            return JsonResponse({'success': False, 'error': 'Bucket name, template bucket name, or PDF name not provided'}, status=400)

        s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                          region_name=settings.AWS_REGION)

        try:
            # Check if the nested "bucket" (prefix) exists
            nested_prefix = f"{template_bucket_name}/{file_name}"
            if prefix_exists(s3, bucket_name, nested_prefix):
                # Fetch the PDF file from S3
                response = s3.get_object(Bucket=bucket_name, Key=nested_prefix)
                pdf_data = response['Body'].read()

                # Return the PDF data as a response
                return HttpResponse(pdf_data, content_type='application/pdf')
            else:
                return JsonResponse({'success': False, 'error': f'PDF file {file_name} not found in template bucket {template_bucket_name}'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


# //////////// fetching whole templateBucket
# @csrf_exempt
# def fetch_and_convert_pdf_from_s3(request, user_bucket_name):
#     if request.method == 'GET':
#         if not user_bucket_name:
#             return JsonResponse({'success': False, 'error': 'User bucket name not provided'}, status=400)

#         s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#                           aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
#                           region_name=settings.AWS_REGION)

#         try:
#             # List objects in the templateBucket
#             response = s3.list_objects_v2(Bucket=user_bucket_name, Prefix='templateBucket/')
#             documents = response.get('Contents', [])

#             result = []

#             for doc in documents:
#                 file_key = doc['Key']
#                 if file_key.endswith('.pdf'):
#                     # Fetch the PDF file from S3
#                     pdf_response = s3.get_object(Bucket=user_bucket_name, Key=file_key)
#                     pdf_data = pdf_response['Body'].read()

#                     # Convert the first page of the PDF to an image
#                     images = convert_from_bytes(pdf_data, first_page=0, last_page=1)
#                     if images:
#                         image = images[0]
#                         buffer = io.BytesIO()
#                         image.save(buffer, format='PNG')
#                         img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
#                         result.append({
#                             'file': file_key,
#                             'image': img_str
#                         })

#             return JsonResponse({'success': True, 'documents': result}, status=200)
#         except Exception as e:
#             return JsonResponse({'success': False, 'error': str(e)}, status=500)
#     else:
#         return JsonResponse({'error': 'Method not allowed'}, status=405)


# @csrf_exempt
# def fetch_and_convert_pdf_from_s3(request, user_bucket_name):
#     if request.method == 'GET':
#         if not user_bucket_name:
#             return JsonResponse({'success': False, 'error': 'User bucket name not provided'}, status=400)

#         s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#                           aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
#                           region_name=settings.AWS_REGION)

#         try:
#             # List objects in the templateBucket
#             response = s3.list_objects_v2(Bucket=user_bucket_name, Prefix='templateBucket/')
#             documents = response.get('Contents', [])

#             result = []

#             for doc in documents:
#                 file_key = doc['Key']
#                 if file_key.endswith('.pdf'):
#                     # Fetch the PDF file from S3
#                     pdf_response = s3.get_object(Bucket=user_bucket_name, Key=file_key)
#                     pdf_data = pdf_response['Body'].read()

#                     # Open the PDF file with PyMuPDF
#                     pdf_document = fitz.open(stream=pdf_data, filetype='pdf')
#                     if pdf_document.page_count > 0:
#                         first_page = pdf_document.load_page(0)
#                         pix = first_page.get_pixmap()
#                         img_data = pix.tobytes()
#                         img_str = base64.b64encode(img_data).decode('utf-8')
#                         result.append({
#                             'file': file_key,
#                             'image': img_str
#                         })

#             return JsonResponse({'success': True, 'documents': result}, status=200)
#         except Exception as e:
#             return JsonResponse({'success': False, 'error': str(e)}, status=500)
#     else:
#         return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def fetch_and_convert_pdf_from_s3(request, user_bucket_name):
    if request.method == 'GET':
        if not user_bucket_name:
            return JsonResponse({'success': False, 'error': 'User bucket name not provided'}, status=400)

        s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                          region_name=settings.AWS_REGION)

        try:
            # List objects in the templateBucket
            response = s3.list_objects_v2(Bucket=user_bucket_name, Prefix='templateBucket/')
            documents = response.get('Contents', [])

            result = []

            for doc in documents:
                file_key = doc['Key']
                if file_key.endswith('.pdf'):
                    # Fetch the PDF file from S3
                    pdf_response = s3.get_object(Bucket=user_bucket_name, Key=file_key)
                    pdf_data = pdf_response['Body'].read()

                    # Open the PDF file with PyMuPDF
                    pdf_document = fitz.open(stream=pdf_data, filetype='pdf')
                    if pdf_document.page_count > 0:
                        first_page = pdf_document.load_page(0)
                        pix = first_page.get_pixmap()
                        img_data = pix.tobytes()
                        img_str = base64.b64encode(img_data).decode('utf-8')

                        # Extract template ID from file_key
                        # Assuming the file key format is something like 'templateBucket/<template_id>-<file_name>.pdf'
                        parts = file_key.split('/')
                        if len(parts) > 1:
                            file_name = parts[-1]
                            template_id = file_name.split('-')[0]  # Extract the part before the hyphen
                        else:
                            template_id = 'Unknown'  # Default value if parsing fails

                        result.append({
                            'file': file_key,
                            'image': img_str,
                            'template_id': template_id
                        })

            return JsonResponse({'success': True, 'documents': result}, status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


import boto3
from botocore.exceptions import ClientError
from django.http import HttpResponse, JsonResponse
from django.conf import settings
 
@api_view(['GET'])
@log_api_request
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
        response = s3_client.generate_presigned_url('get_object',Params={'Bucket': bucket_name,'Key': file_name},ExpiresIn=3600)
    except ClientError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': True, 'url': response})

@csrf_exempt
@api_view(['DELETE'])
@log_api_request
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
 

@csrf_exempt
@api_view(['DELETE'])
@log_api_request
def delete_template_from_s3(request):
    bucket_name = request.data.get('bucket_name')
    file_name = request.data.get('file_name')

    if not bucket_name or not file_name:
        return JsonResponse({'success': False, 'error': 'Bucket name or file name not provided'}, status=400)

    # Add the templateBucket prefix to the file name
    template_key = f'templateBucket/{file_name}'

    s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                      region_name=settings.AWS_REGION)

    try:
        s3.delete_object(Bucket=bucket_name, Key=template_key)
        return JsonResponse({'success': True, 'message': 'Template file deleted successfully'})
    except ClientError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)