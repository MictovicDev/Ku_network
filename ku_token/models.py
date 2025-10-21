from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _




User = get_user_model()
# Create your models here.

class Token(models.Model):
    total_token = models.PositiveBigIntegerField(blank=True, null=True)
    owner = models.OneToOneField(User, verbose_name=_("Token_Owner"), on_delete=models.CASCADE, blank=True, null=True)
    
    
    def __str__(self):
        return f"{self.owner.username} Token"