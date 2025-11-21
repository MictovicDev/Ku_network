from django.shortcuts import render
from rest_framework.views import APIView
from .models import Referral

# Create your views here.
from rest_framework.response import Response
from .serializers import ReferralSerializer
from rest_framework.permissions import IsAuthenticated


class GetReferral(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            referral = Referral.objects.filter(referrer=request.user)
            serializer = ReferralSerializer(referral, many=True)
            return Response({"status": "success", "data": serializer.data}, status=200)
        except Exception as e:
            return Response({"status": "failed", "data": str(e)}, status=400)
