from rest_framework.serializers import ModelSerializer
from .models import MiningSession


class MiningSerializer(ModelSerializer):

    class Meta:
        model = MiningSession
        fields = "__all__"
