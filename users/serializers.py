from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from users.models import User, PasswordResetToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
from phonenumber_field.serializerfields import PhoneNumberField
from django.contrib.auth import get_user_model
from .models import LoginAttempt, UserProfile
from django.contrib.auth import authenticate
from rest_framework.response import Response


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    code = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('email', 'phone_number', 'password',
                  'password2', 'code')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data, **kwargs):
        validated_data.pop('password2')
        # secret = kwargs.get('secret')
        # print(secret)
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            phone_number=validated_data['phone_number']
        )
        return user


class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.CharField()
        self.fields.pop('username', None)

    def validate(self, attrs):
        # Use Django's authenticate to handle user validation
        credentials = {
            'email': attrs.get('email'),
            'password': attrs.get('password')
        }
        user = authenticate(**credentials)

        if user is None:
            raise serializers.ValidationError(
                'Invalid credentials', code='authentication')

        # Generate token and add custom claims
        refresh = self.get_token(user)
        return {
            'id': str(user.id),
            'username': user.username,
            'usertype': user.user_type,
            'token': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
        }

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['user_type'] = user.user_type
        return token


class ActivateAccountSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=10)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['image', 'bio']


class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    profile = UserProfileSerializer()
    
    class Meta:
        model = User
        fields = ('id', 'username', 'phone_number','profile')



class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating both user and profile information"""
    username = serializers.CharField(source='user.username', required=False)

    class Meta:
        model = UserProfile
        fields = ['bio', 'image', 'username']

    def validate_username(self, value):
        """Ensure username is unique and non-empty"""
        if not value.strip():
            raise serializers.ValidationError("Username cannot be empty.")
        if User.objects.filter(username=value).exclude(pk=self.instance.user.pk).exists():
            raise serializers.ValidationError(
                "This username is already taken.")
        return value

    def validate_bio(self, value):
        if value and len(value) < 10:
            raise serializers.ValidationError(
                "Bio must be at least 10 characters long.")
        return value

    def update(self, instance, validated_data):
        """Custom update to handle nested user field"""
        user_data = validated_data.pop('user', {})

        # Update profile fields
        instance.bio = validated_data.get('bio', instance.bio)
        instance.image = validated_data.get('image', instance.image)
        instance.save()

        # Update user fields (like username)
        if user_data:
            user = instance.user
            username = user_data.get('username')
            if username:
                user.username = username
                user.save()

        return instance
