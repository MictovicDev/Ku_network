from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import ClaimTaskSerializer, TaskSerializer, RecentEarningsSerialzer
from datetime import datetime
from .models import Task, RecentEarnings
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from apps.ku_token.models import Token


# Create your views here.


class ClaimMinedToken(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        data = request.data
        serializer = ClaimTaskSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                
                validated_data = serializer.validated_data
                task = get_object_or_404(Task, id=pk, is_active=True)
                claimed_users = task.claimed_users.all()
                if request.user in claimed_users:
                    return Response({"success": "false", "message": "Token Claimed by You"})
                token = Token.objects.get(owner=request.user)
                token.total_token += task.reward_tokens
                token.save()
                task.claimed_users.add(request.user)
                RecentEarnings.objects.create(task=task, user=request.user)
                return Response(
                    {"success": "True", "message": "Token Claimed Successfully"}
                )
            except Exception as e:
                return Response(
                    {"success": "False", "message": str(e)}
                )




class RecentEarningView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RecentEarningsSerialzer
    
    def get(self, request):
        earnings = RecentEarnings.objects.filter(user=request.user)
        serializer = self.serializer_class(earnings, many=True)
        return Response({
            "message": "success",
            "data": serializer.data
        })
    
        
class GetCompletedTask(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer
    
    def get(self, request):
        completed_task = Task.objects.filter(claimed_users=request.user)
        serializer = self.serializer_class(completed_task, many=True)
        return Response({
            "message": "success",
            "data": serializer.data
        })

        

class ClaimTaskToken(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        task = Task.objects.get(id=pk)
        claimed_users = task.claimed_users.all()
        token = Token.objects.get(user=request.user)
        if request.user in claimed_users:
            return Response(
                {"status": "failed", "message": "Task Claimed Already by you"}
            )
        token.quantity += task.reward_tokens
        token.save()
        return Response({"status": "success", "message": "Task claimed Succesfully"})


class ListTask(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        task = Task.objects.exclude(claimed_users=request.user)
        print(task)
        serializer = TaskSerializer(task, many=True, context={"request": request})
        return Response({"message": "true", "data": serializer.data})
