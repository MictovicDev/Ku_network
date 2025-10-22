# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import RegionalLeaderBoard, GlobalLeaderboard
from .serializers import RegionalLeaderBoardSerializer, GlobalLeaderBoardSerializer


class RegionalLeaderboardView(APIView):
    def get(self, request):
        region = request.query_params.get(
            'region')  # or request.GET.get('region')
        
        if region:
            leaderboards = RegionalLeaderBoard.objects.filter(
                region__region_name__iexact=region)
        else:
            leaderboards = RegionalLeaderBoard.objects.all()

        serializer = RegionalLeaderBoardSerializer(leaderboards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GlobalLeaderboardView(APIView):
    def get(self, request):
        leaderboards = GlobalLeaderboard.objects.all()
        serializer = GlobalLeaderBoardSerializer(leaderboards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
