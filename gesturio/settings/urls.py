from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from .views import *

urlpatterns = [
    path('password/', PasswordChangeView.as_view(), name='password-change'),
    path('notifications/', NotificationsView.as_view(), name='notifications'),
    path('preferences/', PreferencesView.as_view(), name='preferences'),
    path('privacy/', PrivacyView.as_view(), name='privacy'),
    path('accounts/delete/', DeleteAccountView.as_view(), name='delete-account'),
]
