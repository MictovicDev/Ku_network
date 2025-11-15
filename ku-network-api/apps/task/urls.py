from django.urls import path
from .views import ClaimToken, ListTask


urlpatterns = [
    path("claim-token/", ClaimToken.as_view(), name="tasks"),
    path("", ListTask.as_view(), name="list-task"),
]
