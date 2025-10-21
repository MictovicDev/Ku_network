from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers


class ClaimTokenSerializer(Serializer):
    
    
    type = serializers.CharField()