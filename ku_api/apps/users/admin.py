from django.contrib import admin
from apps.users.models import UserProfile, User

# Register your models here.
admin.site.register(User)
admin.site.register(UserProfile)
