from rest_framework.parsers import JSONParser
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from mainapp.models import User,RecipientRole,BulkPdfDocumentTable,BulkPdfRecipientDetail
from mainapp.serializers import BulkDocumentTableSerializer

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
