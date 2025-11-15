from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from .models import Task


class ClaimTaskSerializer(ModelSerializer):

    class Meta:
        model = Task
        fields = ["id", "title", "category"]

    def validate(self, attrs):
        title = attrs.get("title")
        category = attrs.get("category")

        try:
            task = Task.objects.get(title=title, category=category)
        except Task.DoesNotExist:
            raise serializers.ValidationError("Task Doesn't exist")

        return attrs


class TaskSerializer(ModelSerializer):
    images = serializers.ImageField()

    class Meta:
        model = Task
        exclude = ["claimed_users", "is_active"]
