from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
import uuid
from .manager import UserManager
from django.core.validators import EmailValidator
import secrets
from django.utils import timezone
from datetime import timedelta
from phonenumber_field.modelfields import PhoneNumberField
import uuid

# from cloudinary.models import CloudinaryField
import random
import string
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Region(models.Model):
    """Regions for user classification"""

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    """Extended User Model"""

    USER_TYPE_CHOICES = [
        ("regular", "Regular"),
        ("premium", "Premium"),
    ]

    referred_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="referrals",
    )
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True
    )
    username = models.CharField(max_length=250, unique=True, db_index=True)
    email = models.EmailField(
        unique=True,
        db_index=True,
        validators=[
            EmailValidator(message="Enter a valid email address"),
        ],
    )
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    phone_number = PhoneNumberField(blank=True, null=True)
    secret = models.CharField(max_length=500, blank=True, null=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    full_name = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True, max_length=500)
    profile_picture = models.ImageField(
        upload_to="profile_pics/", blank=True, null=True
    )

    # Auto-generated but editable username
    username = models.CharField(max_length=150, unique=True)

    # Authentication
    google_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    is_verified = models.BooleanField(default=False)
    user_type = models.CharField(
        max_length=20, choices=USER_TYPE_CHOICES, default="regular"
    )

    # KYC
    is_kyc_verified = models.BooleanField(default=False)
    kyc_submitted_at = models.DateTimeField(null=True, blank=True)
    kyc_verified_at = models.DateTimeField(null=True, blank=True)

    # Region
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
    # Referral System
    referral_code = models.CharField(max_length=20, unique=True, blank=True)
    referred_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referrals",
    )
    referral_bonus_received = models.BooleanField(default=False)

    # Mining
    total_ku_earned = models.DecimalField(
        max_digits=20, decimal_places=4, default=Decimal("0.0000")
    )
    current_mining_speed = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal("0.2083"),  # Base rate: 0.2083 tokens/hour
        help_text="Tokens per hour",
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    # REQUIRED_FIELDS = ['fullnam']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def is_online(self):
        if not self.last_seen:
            return False
        return timezone.now() - self.last_seen < timedelta(minutes=5)

    def save(self, *args, **kwargs):
        # Auto-generate username if not provided
        if not self.username:
            self.username = f"user_{self.email.split('@')[0]}_{uuid.uuid4().hex[:6]}"

        # Auto-generate referral code if not provided
        if not self.referral_code:
            self.referral_code = f"KU{uuid.uuid4().hex[:8].upper()}"

        super().save(*args, **kwargs)

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def total_team_members(self):
        """Get total number of direct referrals"""
        return self.referrals.count()

    @property
    def verified_team_members(self):
        """Get number of verified referrals"""
        return self.referrals.filter(is_verified=True).count()

    def calculate_mining_speed(self):
        """
        Calculate dynamic mining speed based on referrals
        Base: 0.2083 tokens/hour
        +0.05 tokens/hour per referral
        +0.1 tokens/hour per verified referral
        """
        base_speed = Decimal("0.2083")
        referral_count = self.total_team_members
        verified_count = self.verified_team_members

        # Bonus from referrals
        referral_bonus = Decimal(str(referral_count)) * Decimal("0.05")
        verified_bonus = Decimal(str(verified_count)) * Decimal("0.1")

        new_speed = base_speed + referral_bonus + verified_bonus

        # Cap at 5 tokens/hour
        if new_speed > Decimal("5.0"):
            new_speed = Decimal("5.0")

        self.current_mining_speed = new_speed
        self.save(update_fields=["current_mining_speed"])
        return new_speed


class PasswordResetToken(models.Model):
    """Store tokens for password reset"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="password_reset_tokens"
    )
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_hex(32)

        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=30)

        super().save(*args, **kwargs)

    def is_valid(self):
        """Check if the token is valid (not expired and not used)"""
        return not self.used and self.expires_at > timezone.now()

    class Meta:
        indexes = [
            models.Index(fields=["token"]),
            models.Index(fields=["user"]),
            models.Index(fields=["expires_at"]),
        ]


class LoginAttempt(models.Model):
    email = models.EmailField()
    success = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True)

    def __str__(self):
        return f"Login attempt for {self.email} at {self.timestamp} ({'Success' if self.success else 'Failed'})"

    @classmethod
    def check_failed_attempts(cls, email, time_window_minutes=15, max_attempts=5):
        from django.utils import timezone
        from datetime import timedelta

        time_threshold = timezone.now() - timedelta(minutes=time_window_minutes)
        failed_attempts = cls.objects.filter(
            email=email, success=False, timestamp__gte=time_threshold
        ).count()
        return failed_attempts >= max_attempts


class UserProfile(models.Model):
    """Extended profile information"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="profile_pictures", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
