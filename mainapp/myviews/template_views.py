from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.http import JsonResponse 

from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Exists, OuterRef
from django.shortcuts import get_object_or_404

from mainapp.myviews.user_views import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from mainapp.models import Template,TemplateDraggedData,UseTemplateRecipient
from mainapp.serializers import TemplateSerializer,TemplateDraggedData,TemplateRecipient,TemplateDraggedSerializer,UseTemplateRecipient,UseTemplateRecipientSerializer,TemplateRecipientSerializer

class TemplateViewSet(viewsets.ModelViewSet):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    def get_queryset(self):
        user = self.request.user
        # Subquery to check existence of template_id in TemplateDraggedData
        dragged_data_exists = TemplateDraggedData.objects.filter(template_id=OuterRef('pk')).values('id')

        # Filter templates created by the user and exist in TemplateDraggedData
        queryset = Template.objects.filter(
            created_by=user
        ).filter(
            Exists(dragged_data_exists)
        )

        # Delete templates that do not exist in TemplateDraggedData
        templates_to_delete = Template.objects.filter(
            created_by=user
        ).exclude(
            Exists(dragged_data_exists)
        )
        templates_to_delete.delete()

        return queryset

    def create(self, request, *args, **kwargs):
        template_name = request.data.get('templateName')
        userid = request.data.get('created_by')

        existing_template = Template.objects.filter(
            templateName=template_name, created_by=userid
        ).exists()

        if existing_template:
            return Response(
                {"error": "Template with the same name already exists for this user."},
                status=status.HTTP_400_BAD_REQUEST
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
 