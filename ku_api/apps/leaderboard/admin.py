from django.contrib import admin
from .models import GlobalLeaderboard, RegionalLeaderBoard, Region

# Register your models here.

admin.site.register(GlobalLeaderboard)
admin.site.register(Region)
admin.site.register(RegionalLeaderBoard)
