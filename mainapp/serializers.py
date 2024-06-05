from rest_framework import serializers
from .models import User,Template,TemplateDraggedData,TemplateRecipient,DocumentTable,UseTemplateRecipient,DocumentRecipientDetail,RecipientPositionData
from send_mail_app.models import EmailList
from .models import *

# class AuthSerializer(serializers.Serializer):
#     code = serializers.CharField(required=False)
#     error = serializers.CharField(required=False)

# /// sakshi serializers
class EmailListSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailList
        fields = ['id', 'emails', 'status', 'docId']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'full_name', 'initial', 'stamp_img_name', 'stamp_enc_key', 's3Key','profile_pic']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = ['template_id', 'templateName', 'createTempfile','templateNumPages','created_by']

class TemplateDraggedSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateDraggedData
        fields = '__all__'
        
class TemplateRecipientSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateRecipient
        fields = '__all__'
        print("Fields:", fields) 

class DocumentTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTable
        fields = '__all__'

class UseTemplateRecipientSerializer(serializers.ModelSerializer):
    class Meta:
        model = UseTemplateRecipient
        fields = '__all__'

class DocumentRecipientSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentRecipientDetail
        fields = '__all__'

class DocumentPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipientPositionData
        fields = '__all__'

class DocumentSerializer(serializers.ModelSerializer):
    creator_id = UserSerializer()
    last_modified_by = UserSerializer()
    class Meta:
        model = DocumentTable
        fields = '__all__'

class UserSignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signature
        fields = '__all__'
 
class UserInitialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Initials
        fields = '__all__'

class BulkDocumentTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = BulkPdfDocumentTable
        fields = '_all_'