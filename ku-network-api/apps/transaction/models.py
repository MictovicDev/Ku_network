from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


# Create your models here.
class Transaction(models.Model):
    """Track all token transactions"""

    TRANSACTION_TYPE_CHOICES = [
        ("mining", "Mining Reward"),
        ("referral", "Referral Bonus"),
        ("task", "Task Completion"),
        ("bonus", "Bonus"),
        ("withdrawal", "Withdrawal"),
        ("transfer", "Transfer"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="transactions"
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=20, decimal_places=4)

    description = models.CharField(max_length=255)
    reference_id = models.UUIDField(default=uuid.uuid4, unique=True)

    balance_before = models.DecimalField(max_digits=20, decimal_places=4)
    balance_after = models.DecimalField(max_digits=20, decimal_places=4)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["transaction_type"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount}"
