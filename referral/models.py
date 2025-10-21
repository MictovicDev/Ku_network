from django.db import models
from decimal import Decimal
from django.contrib.auth import get_user_model



User = get_user_model()

# Create your models here.
class Referral(models.Model):
    """Track referral bonuses"""
    referrer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='referral'
    )
    referred_user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='referral_bonus_received_from'
    )
    
    immediate_bonus = models.DecimalField(
        max_digits=10, 
        decimal_places=4, 
        default=Decimal('5.0000'),
        help_text="Immediate 5 token bonus"
    )
    verification_bonus = models.DecimalField(
        max_digits=10, 
        decimal_places=4, 
        default=Decimal('0.0000'),
        help_text="Bonus when referred user verifies"
    )
    
    is_verified_bonus_claimed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    verified_bonus_claimed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['referrer', 'referred_user']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.referrer.username} referred {self.referred_user.username}"
