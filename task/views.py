from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import ClaimTaskSerializer, TaskSerializer
from datetime import datetime
from .models import Task
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from ku_token.models import Token
# Create your views here.


class ClaimToken(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        serializer = ClaimTaskSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            title = validated_data.get('title')
            category = validated_data.get('category')
            id = validated_data.get('id')
            task = get_object_or_404(
                Task, title=title, category=category, id=id, is_active=True)
            claimed_users = task.claimed_users.all()
            if request.user in claimed_users:
                return Response({
                    "success": "false",
                    "message": "Token Claimed by You"
                })
            token = Token.objects.get(owner=request.user, task=task)
            token.total_token += task.reward_tokens
            token.save()
            task.claimed_users.add(request.user)
            return Response({
                "success": "True",
                "message": "Token Claimed Successfully"
            })


class ListTask(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        task = Task.objects.exclude(claimed_users=request.user)
        print(task)
        serializer = TaskSerializer(task, many=True, context={"request": request})
        return Response({
            "message": "true",
            "data": serializer.data
        })
