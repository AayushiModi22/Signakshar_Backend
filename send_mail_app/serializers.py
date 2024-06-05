from rest_framework import serializers
from .models import EmailList

class EmailListSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailList
        fields = '__all__'
