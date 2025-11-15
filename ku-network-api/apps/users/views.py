from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, ActivateAccountSerializer, InvitationSerializer
from django.contrib.auth import get_user_model
from .serializers import UserTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from apps.users.utils.otp import OTPManager
from apps.users.utils.email import EmailManager
from celery import shared_task
from rest_framework.throttling import AnonRateThrottle
from django.template.loader import render_to_string
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .models import LoginAttempt
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework import permissions
from .models import UserProfile
from django.contrib.auth.hashers import check_password
import logging
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

# from django.contrib.auth import authenticate
# from .tasks import send_welcome_email_async
from rest_framework.parsers import MultiPartParser, FormParser
from .models import UserProfile
from .serializers import UserProfileGetUpdateSerializer, UserProfileSerializer
from apps.referral.models import Referral
from django.shortcuts import get_object_or_404
from apps.ku_token.models import Token

logger = logging.getLogger(__name__)
User = get_user_model()


class UserTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
            logger.info(f"User found: {user.email}")

            # Authenticate manually using the serializer
            serializer = TokenObtainPairSerializer(
                data={
                    "email": user.email,
                    "password": password,
                }
            )
            print(user.email)
            if serializer.is_valid():
                return Response(
                    {
                        "id": str(user.id),
                        "email": user.email,
                        "user_type": getattr(user, "user_type", None),
                        "token": serializer.validated_data,
                    }
                )
            else:
                return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

        except User.DoesNotExist:
            logger.warning(f"Login attempt with non-existent email: {email}")
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            logger.error(f"Login error for {email}: {str(e)}")
            return Response(
                {"error": "Login failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DeleteAccountView(APIView):
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            user.is_active = False
            user.save()
            return Response({"Message": "Account Deleted Successfully"}, status=200)
        except Exception as e:
            return Response({"Message": "Error Deleting Account"}, status=400)


class RegisterView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                otp_m = OTPManager()
                code = serializer.validated_data["code"]
                print(code)
                secret = otp_m.get_secret()
                otp = otp_m.generate_otp()
                user = serializer.save()
                user.secret = secret
                user.is_active = True
                referrer = get_object_or_404(User, referral_code=code)
                user.save()
                if code:
                    Referral.objects.create(
                        referrer=referrer, referred_user=user)
                UserProfile.objects.create(user=user)
                Token.objects.create(owner=user, total_token=0)
                return Response(
                    {
                        "message": "success",
                        "user": {
                            "email": user.email,
                            "phone_number": str(user.phone_number),
                        },
                    },
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                print(e)
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SetInvitationCodeView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InvitationSerializer

    def post(self, request):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                print(serializer.validated_data)
                code = serializer.validated_data.get("code")
                print(code)
                user.referral_code = code
                user.save()
                return Response({
                    "status": "success",
                    "data": serializer.data
                })
            except Exception as e:
                print(e)
                return Response(
                    {"status": "failed", "error": "Invalid data"}, status=400
                )


class ActivateAccountView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ActivateAccountSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        otp_code = serializer.validated_data["otp"]

        try:
            user = User.objects.get(email=email)

            if user.is_active:
                return Response(
                    {"message": "Already Verified, Login"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user_secret = user.secret

            if OTPManager(user_secret).verify_otp(otp_code):
                user.is_active = True
                user.save()

                token = UserTokenObtainPairSerializer().get_token(user)

                return Response(
                    {
                        "user": user.email,
                        "user_type": user.user_type,
                        "token": {
                            "access": str(token.access_token),
                            "refresh": str(token),
                        },
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"message": "Invalid or expired OTP"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except User.DoesNotExist:
            return Response(
                {"message": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )


class UserProfileGetUpdateView(APIView):
    """API endpoint for updating user profile and username"""

    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        """Retrieve the authenticated user's profile"""
        try:
            profile = UserProfile.objects.select_related(
                "user").get(user=request.user)
            serializer = UserProfileGetUpdateSerializer(
                profile, context={"request": request}
            )
            return Response(
                {"message": "success", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        except UserProfile.DoesNotExist:
            return Response(
                {"detail": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """Partially update profile and username"""
        try:
            profile = UserProfile.objects.select_related(
                "user").get(user=request.user)
            serializer = UserProfileGetUpdateSerializer(
                profile, data=request.data, partial=True
            )

            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"message": "success", "data": serializer.data},
                    status=status.HTTP_200_OK,
                )

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except UserProfile.DoesNotExist:
            return Response(
                {"detail": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ForgotPassword(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not user.check_password(old_password):
            return Response(
                {"detail": "Old password is incorrect"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(new_password, user)
        except Exception as e:
            return Response({"detail": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response(
            {"detail": "Password updated successfully"}, status=status.HTTP_200_OK
        )


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not user.check_password(old_password):
            return Response(
                {"detail": "Old password is incorrect"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(new_password, user)
        except Exception as e:
            return Response({"detail": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response(
            {"detail": "Password updated successfully"}, status=status.HTTP_200_OK
        )
