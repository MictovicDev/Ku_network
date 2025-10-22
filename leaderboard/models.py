from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.



User = get_user_model()



class Region(models.Model):
    region_name = models.CharField(max_length=250, blank=True, null=True)
    region_codle = models.CharField(max_length=250,blank=True, null=True)
    
    
    def __str__(self):
        return f"{self.region_name} - {self.region_codle}"
    
    

class RegionalLeaderBoard(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='regional_leaderboard')
    rank_regional = models.IntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    team_size = models.IntegerField(default=0)
    
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-total_earnings']
        indexes = [
            models.Index(fields=['total_earnings']),
        ]

    def __str__(self):
        return f"{self.user.username} - Rank #{self.rank_regional}"

    

class GlobalLeaderboard(models.Model):
    """Cached leaderboard data for performance"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='global_leaderboard')
    rank_global = models.IntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    team_size = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['total_earnings']
        indexes = [
            models.Index(fields=['total_earnings']),
        ]

    def __str__(self):
        return f"{self.user.username} - Rank #{self.rank_global}"
