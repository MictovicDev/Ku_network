from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
import logging 
from ku_token.models import Token


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)




User = get_user_model()

@receiver(post_save, sender=Token)
def create_user_profile(sender, instance, created, **kwargs):
    """
    
    """
    if not created:
        token = instance.owner
        
        