from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.



User = get_user_model()

class Leaderboard(models.Model):
    """Cached leaderboard data for performance"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='leaderboard_entry')
    rank_global = models.IntegerField(default=0)
    rank_regional = models.IntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=20, decimal_places=4)
    team_size = models.IntegerField(default=0)
    
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['rank_global']
        indexes = [
            models.Index(fields=['rank_global']),
            models.Index(fields=['rank_regional']),
        ]

    def __str__(self):
        return f"{self.user.username} - Rank #{self.rank_global}"
