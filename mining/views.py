from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import MiningSerializer
# Create your views here.



class UpdateMiningActivity(APIView):
    permission_classes = [IsAuthenticated]
    
    
    def post(self, request):
        serializer = MiningSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()