from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
# Create your views here.


class ClaimToken(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        data = request.data
        serializer = ClaimTokenSerializer(data=data)