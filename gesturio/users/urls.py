from django.contrib import admin
from django.urls import path
from .oauth import GoogleLoginView, GoogleCallbackView, MicrosoftLoginView, MicrosoftCallbackView
from .views import Login, RegisterAuth, UpdateProfile, Logout

urlpatterns = [
    path("register/", RegisterAuth.as_view(), name="register"),
    path("update/", UpdateProfile.as_view(), name="update"),
    path("logout/", Logout.as_view(), name="logout"),
    # path("refresh/", RefreshTokenView.as_view(), name="refresh"),
    # path("profile/", ProfileView.as_view(), name="profile"),
    path("login/", Login.as_view(), name="login"),
    path("google/login/", GoogleLoginView.as_view(), name="google-login"),
    path("google/login/callback/", GoogleCallbackView.as_view(), name="google-callback"),
    path("microsoft/login/", MicrosoftLoginView.as_view(), name="microsoft-login"),
    path("microsoft/callback/", MicrosoftCallbackView.as_view(), name="microsoft-callback"),
]