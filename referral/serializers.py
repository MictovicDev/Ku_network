from rest_framework.serializers import ModelSerializer
from .models import Referral
from users.serializers import UserSerializer





class ReferralSerializer(ModelSerializer):
    referrer = UserSerializer()
    referred_user = UserSerializer()
    class Meta:
        model = Referral
        fields = '__all__'