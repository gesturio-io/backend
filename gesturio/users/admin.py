from django.contrib import admin

from .models import UserAuth, UserProfile

admin.site.register(UserAuth)
admin.site.register(UserProfile)
