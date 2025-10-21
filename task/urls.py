from django.urls import path
from .views import ClaimToken


urlpatterns = [
    path("claim-token/", ClaimToken.as_view(), name="tasks")
]
