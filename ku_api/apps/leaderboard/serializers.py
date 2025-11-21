from rest_framework.serializers import ModelSerializer
from .models import RegionalLeaderBoard, GlobalLeaderboard


class RegionalLeaderBoardSerializer(ModelSerializer):

    class Meta:
        model = RegionalLeaderBoard
        fields = "__all__"


class GlobalLeaderBoardSerializer(ModelSerializer):

    class Meta:
        model = GlobalLeaderboard
        fields = "__all__"
