from rest_framework.views import APIView
from rest_framework.response import Response 
from django.db.models import Q, Exists, OuterRef
from rest_framework import status
from django.shortcuts import get_object_or_404

from send_mail_app.models import EmailList
from mainapp.myviews.user_views import JWTAuthentication
from mainapp.models import User,DocumentTable,DocumentRecipientDetail,RecipientPositionData
from mainapp.serializers import DocumentSerializer,DocumentRecipientSerializer,EmailListSerializer
from ..decorators.logging import log_api_request 
from django.utils.decorators import method_decorator

# class DocumentView2(APIView):
#     @method_decorator(log_api_request)
#     def post(self, request, format=None):
#         print("dashboard_views DocumentView2")
#         created_by_you = request.data.get('createdByYou')
#         created_by_others = request.data.get('createdByOthers')
#         user_id = request.data.get('userid')

#         if not user_id:
#             return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             email = User.objects.get(id=user_id).email
#         except User.DoesNotExist:
#             return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

#         # Subquery to check existence of docId in RecipientPositionData
#         recipient_position_data_exists = RecipientPositionData.objects.filter(docId=OuterRef('pk')).values('id')

#         if created_by_you and created_by_others:
#             documents = DocumentTable.objects.filter(
#                 (Q(creator_id=user_id) |
#                  Q(id__in=DocumentRecipientDetail.objects.filter(email=email).values_list('docId', flat=True))) &
#                 Exists(recipient_position_data_exists)
#             ).select_related('creator_id', 'last_modified_by')
#         elif created_by_you:
#             documents = DocumentTable.objects.filter(
#                 Q(creator_id=user_id) &
#                 Exists(recipient_position_data_exists)
#             ).select_related('creator_id', 'last_modified_by')
#         elif created_by_others:
#             documents = DocumentTable.objects.filter(
#                 Q(id__in=DocumentRecipientDetail.objects.filter(email=email).values_list('docId', flat=True)) &
#                 ~Q(creator_id=user_id) &
#                 Exists(recipient_position_data_exists)
#             ).select_related('creator_id', 'last_modified_by')
#         else:
#             return Response({"error": "Invalid request parameters"}, status=status.HTTP_400_BAD_REQUEST)

#         # Deleting documents whose docId does not exist in RecipientPositionData
#         documents_to_delete = DocumentTable.objects.filter(
#             ~Exists(recipient_position_data_exists)
#         )
#         documents_to_delete.delete()

#         serializer = DocumentSerializer(documents, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)


# class DocumentView2(APIView):
#     # @method_decorator(log_api_request)
#     # def dispatch(self, request, *args, **kwargs):
#     #     return super().dispatch(request, *args, **kwargs)

#     def post(self, request, format=None):
#         print("dashboard_views DocumentView2")
#         created_by_you = request.data.get('createdByYou')
#         created_by_others = request.data.get('createdByOthers')
#         user_id = request.data.get('userid')

#         if not user_id:
#             return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             email = User.objects.get(id=user_id).email
#         except User.DoesNotExist:
#             return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

#         recipient_position_data_exists = RecipientPositionData.objects.filter(docId=OuterRef('pk')).values('id')

#         if created_by_you and created_by_others:
#             documents = DocumentTable.objects.filter(
#                 (Q(creator_id=user_id) |
#                  Q(id__in=DocumentRecipientDetail.objects.filter(email=email).values_list('docId', flat=True))) &
#                 Exists(recipient_position_data_exists)
#             ).select_related('creator_id', 'last_modified_by')
#         elif created_by_you:
#             documents = DocumentTable.objects.filter(
#                 Q(creator_id=user_id) &
#                 Exists(recipient_position_data_exists)
#             ).select_related('creator_id', 'last_modified_by')
#         elif created_by_others:
#             documents = DocumentTable.objects.filter(
#                 Q(id__in=DocumentRecipientDetail.objects.filter(email=email).values_list('docId', flat=True)) &
#                 ~Q(creator_id=user_id) &
#                 Exists(recipient_position_data_exists)
#             ).select_related('creator_id', 'last_modified_by')
#         else:
#             return Response({"error": "Invalid request parameters"}, status=status.HTTP_400_BAD_REQUEST)

#         # Deleting documents whose docId does not exist in RecipientPositionData
#         documents_to_delete = DocumentTable.objects.filter(
#             ~Exists(recipient_position_data_exists)
#         )
#         documents_to_delete.delete()

#         serializer = DocumentSerializer(documents, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

class DocumentView2(APIView):
    def post(self, request, format=None):
        print("dashboard_views DocumentView2")
        created_by_you = request.data.get('createdByYou')
        created_by_others = request.data.get('createdByOthers')
        user_id = request.data.get('userid') #logged in 
        

        if not user_id:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            email = User.objects.get(id=user_id).email
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        recipient_position_data_exists = RecipientPositionData.objects.filter(docId=OuterRef('pk')).values('id')

        if created_by_you and created_by_others:
            documents = DocumentTable.objects.filter(
                (Q(creator_id=user_id) |
                 Q(id__in=DocumentRecipientDetail.objects.filter(email=email).values_list('docId', flat=True))) &
                Exists(recipient_position_data_exists)
            ).select_related('creator_id', 'last_modified_by')
        elif created_by_you:
            documents = DocumentTable.objects.filter(
                Q(creator_id=user_id) &
                Exists(recipient_position_data_exists)
            ).select_related('creator_id', 'last_modified_by')
        elif created_by_others:
            documents = DocumentTable.objects.filter(
                Q(id__in=DocumentRecipientDetail.objects.filter(email=email).values_list('docId', flat=True)) &
                ~Q(creator_id=user_id) &
                Exists(recipient_position_data_exists)
            ).select_related('creator_id', 'last_modified_by')
        else:
            return Response({"error": "Invalid request parameters"}, status=status.HTTP_400_BAD_REQUEST)

        # Deleting documents whose docId does not exist in RecipientPositionData
        documents_to_delete = DocumentTable.objects.filter(
            creator_id=user_id
        ).filter(
            ~Exists(recipient_position_data_exists)
        )
        documents_to_delete.delete()

        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class getRecipientCount(APIView):
    def post(self, request):
        print("dashboard_views getRecipientCount")
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
        print("dashboard_views getRecipientDetails")
        doc_id = request.data.get('docid')
       
        if not doc_id:
            return Response({"error": "Document ID is required"}, status=status.HTTP_400_BAD_REQUEST)
 
        # Querysets for documents created by the user and documents where the user is a recipient
        recipients = DocumentRecipientDetail.objects.filter(docId=doc_id)
 
        serializer = DocumentRecipientSerializer(recipients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
   
class getStatus(APIView):
    def post(self, request, format=None):
        print("dashboard_views getStatus post")
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
        print("dashboard_views getPendingRecipientCount")
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
    @method_decorator(log_api_request)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        print("dashboard_views deleteDocumentView")
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
          

# //// combined document view
 
# properly working but late response
class CombinedDocumentView(APIView):
    def post(self, request, format=None):
        print("dashboard_views DocumentViewMerged")
        created_by_you = request.data.get('createdByYou')
        created_by_others = request.data.get('createdByOthers')
        user_id = request.data.get('userid')  # logged in
 
        if not user_id:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
 
        try:
            email = User.objects.get(id=user_id).email
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
 
        recipient_position_data_exists = RecipientPositionData.objects.filter(docId=OuterRef('pk')).values('id')
 
        if created_by_you and created_by_others:
            documents = DocumentTable.objects.filter(
                (Q(creator_id=user_id) |
                 Q(id__in=DocumentRecipientDetail.objects.filter(email=email).values_list('docId', flat=True))) &
                Exists(recipient_position_data_exists)
            ).select_related('creator_id', 'last_modified_by')
        elif created_by_you:
            documents = DocumentTable.objects.filter(
                Q(creator_id=user_id) &
                Exists(recipient_position_data_exists)
            ).select_related('creator_id', 'last_modified_by')
        elif created_by_others:
            documents = DocumentTable.objects.filter(
                Q(id__in=DocumentRecipientDetail.objects.filter(email=email).values_list('docId', flat=True)) &
                ~Q(creator_id=user_id) &
                Exists(recipient_position_data_exists)
            ).select_related('creator_id', 'last_modified_by')
        else:
            return Response({"error": "Invalid request parameters"}, status=status.HTTP_400_BAD_REQUEST)
 
        # Deleting documents whose docId does not exist in RecipientPositionData
        documents_to_delete = DocumentTable.objects.filter(
            creator_id=user_id
        ).filter(
            ~Exists(recipient_position_data_exists)
        )
        documents_to_delete.delete()
 
        # Get the recipient count and pending count for all documents
        doc_ids = documents.values_list('id', flat=True)
 
        recipient_counts = DocumentRecipientDetail.objects.filter(
            docId__in=doc_ids
        ).values('docId').annotate(recipient_count=Count('id'))
 
        pending_counts = RecipientPositionData.objects.filter(
            Q(docId__in=doc_ids) &
            (Q(reviewer_status='pending') | Q(reviewer_status='sent') | Q(signer_status='pending') | Q(signer_status='sent'))
        ).values('docId').annotate(pending_count=Count('id', distinct=True))
 
        # Combine the document data with recipient and pending counts
        serializer = DocumentSerializer(documents, many=True)
        document_data = serializer.data
 
        for doc in document_data:
            doc_id = doc['id']
            doc['recipient_count'] = next((rc['recipient_count'] for rc in recipient_counts if rc['docId'] == doc_id), 0)
            doc['pending_count'] = next((pc['pending_count'] for pc in pending_counts if pc['docId'] == doc_id), 0)
 
        return Response(document_data, status=status.HTTP_200_OK)