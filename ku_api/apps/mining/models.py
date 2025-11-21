from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.utils.translation import gettext_lazy as _

User = get_user_model()


# Create your models here.
class MiningSession(models.Model):
    """Track mining sessions"""

    SESSION_STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
        ("claimed", "Claimed"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="mining_sessions"
    )
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)

    mining_speed = models.DecimalField(
        max_digits=10, decimal_places=4, help_text="Mining speed at start of session"
    )
    tokens_mined = models.DecimalField(
        max_digits=20, decimal_places=4, default=Decimal("0.0000")
    )

    status = models.CharField(
        max_length=20, choices=SESSION_STATUS_CHOICES, default="active"
    )
    claimed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-start_time"]

    def __str__(self):
        return f"{self.user.username} - {self.start_time} - {self.status}"

    def calculate_tokens(self):
        """Calculate tokens mined in this session (12 hours = 2.5 tokens base)"""
        if self.end_time:
            duration_hours = (self.end_time - self.start_time).total_seconds() / 3600
            self.tokens_mined = Decimal(str(duration_hours)) * self.mining_speed
            self.save(update_fields=["tokens_mined"])
        return self.tokens_mined
