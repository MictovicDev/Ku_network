from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
import logging 
from ku_token.models import Token
from .models import GlobalLeaderboard, RegionalLeaderBoard
from datetime import datetime
from task.models import Task

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)



@receiver(pre_save, sender=Token)
def update_leaderboard_on_token_increase(sender, instance, **kwargs):
    """
    Compare new token value to old value before saving.
    If there's an increase, update leaderboards.
    """
    # Only run if this token already exists (not when creating a new one)
    if not instance.pk:
        return

    try:
        old_instance = Token.objects.get(pk=instance.pk)
    except Token.DoesNotExist:
        return

    old_value = old_instance.total_token
    new_value = instance.total_token

    # Only update leaderboard if token increased
    if new_value > old_value:
        user = instance.owner
        difference = new_value - old_value

        global_lb, _ = GlobalLeaderboard.objects.get_or_create(user=user)
        regional_lb, _ = RegionalLeaderBoard.objects.get_or_create(user=user)

        global_lb.total_earnings += difference
        global_lb.last_updated = datetime.now()
        global_lb.save()

        regional_lb.total_earnings += difference
        regional_lb.last_updated = datetime.now()
        regional_lb.save()

        print(f"Leaderboard updated — token increased by {difference}")