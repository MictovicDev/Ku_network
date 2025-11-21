from django.urls import path
from . import views


urlpatterns = [path("", views.GetReferral.as_view(), name="referrals")]
