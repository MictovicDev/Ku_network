from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Task(models.Model):
    """Tasks for users to complete"""

    TASK_TYPE_CHOICES = [
        ("daily", "Daily Task"),
        ("referral", "Referral Task"),
        ("kyc", "KYC Task"),
        ("social", "Social Media Task"),
        ("custom", "Custom Task"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES)
    reward_tokens = models.DecimalField(max_digits=10, decimal_places=4)
    claimed_users = models.ManyToManyField(User, blank=True)
    is_active = models.BooleanField(default=True)
    required_action = models.CharField(max_length=255, blank=True)
    images = models.ImageField(upload_to="task/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class RecentEarnings(models.Model):
    task = models.ForeignKey(Task, on_delete=models.PROTECT, blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    
    
    
    def __str__(self):
        return self.task
