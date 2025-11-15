# urls.py
from django.urls import path
from .views import RegionalLeaderboardView

urlpatterns = [
    path("regional/", RegionalLeaderboardView.as_view(), name="regional-leaderboard"),
]
