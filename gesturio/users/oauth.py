from django.conf import settings
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from .models import UserAuth, LoginType
from .utils import generate_jwt_token
from django.http import HttpResponseRedirect


class GoogleLoginView(APIView):
    def get(self, request):
        
        google_auth_url = (
            "https://accounts.google.com/o/oauth2/auth"
            "?response_type=code"
            f"&client_id={settings.GOOGLE_CLIENT_ID}"
            "&redirect_uri=" + settings.GOOGLE_REDIRECT_URI +
            "&scope=email profile"
        )
        
        return redirect(google_auth_url)



class GoogleCallbackView(APIView):
    def get(self, request):
        code = request.GET.get("code")
        if not code:
            return Response({"error": "Authorization code not provided"}, status=400)

        # Step 1: Exchange code for token
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        token_res = requests.post(token_url, data=token_data)
        token_json = token_res.json()

        if "access_token" not in token_json:
            return Response({"error": "Failed to get access token"}, status=400)

        access_token = token_json["access_token"]

        # Step 2: Get user info
        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        user_info_res = requests.get(user_info_url, headers={"Authorization": f"Bearer {access_token}"})
        user_info = user_info_res.json()

        email = user_info.get("email")
        name = user_info.get("name")

        if not email:
            return Response({"error": "Failed to retrieve email"}, status=400)

        # Step 3: Register or get user
        user, created = UserAuth.objects.get_or_create(
            email=email,
            defaults={
                "username": email,
                "login_type": LoginType.google
            }
        )

        # Step 4: Generate tokens
        access_token = generate_jwt_token(user)
        refresh_token = generate_jwt_token(user, is_refresh=True)

        # Step 5: Redirect to frontend and set cookies
        redirect_url = settings.FRONTEND_URL
        response = HttpResponseRedirect(redirect_url)
        # response = Response()
        response.set_cookie(
            "jwt",
            access_token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="Lax"
        )
        response.set_cookie(
            "refresh_token",
            refresh_token,
            httponly=True,
            secure=False,
            samesite="Lax"
        )

        return response
    
class MicrosoftLoginView(APIView):
    def get(self, request):
        """Redirect user to Microsoft OAuth login page."""
        microsoft_auth_url = (
            f"{settings.MICROSOFT_AUTH_URL}"
            "?client_id=" + settings.MICROSOFT_CLIENT_ID +
            "&response_type=code"
            "&scope=openid email profile"
            "&redirect_uri=" + settings.MICROSOFT_REDIRECT_URI
        )
        return redirect(microsoft_auth_url)
    
class MicrosoftCallbackView(APIView):
    def get(self, request):
        """Exchange Microsoft OAuth2 code for access token & authenticate user."""
        code = request.GET.get("code")

        if not code:
            return Response({"error": "Authorization code not provided"}, status=400)

        token_data = {
            "client_id": settings.MICROSOFT_CLIENT_ID,
            "client_secret": settings.MICROSOFT_CLIENT_SECRET,
            "code": code,
            "redirect_uri": settings.MICROSOFT_REDIRECT_URI,
            "grant_type": "authorization_code",
            "scope": "openid email profile"
        }
        token_res = requests.post(settings.MICROSOFT_TOKEN_URL, data=token_data)
        token_json = token_res.json()

        if "access_token" not in token_json:
            return Response({"error": "Failed to get access token"}, status=400)

        access_token = token_json["access_token"]

        user_info_res = requests.get(
            settings.MICROSOFT_USER_INFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        user_info = user_info_res.json()

        email = user_info.get("mail") or user_info.get("userPrincipalName")
        name = user_info.get("displayName")

        if not email:
            return Response({"error": "Failed to retrieve email"}, status=400)

        user, created = UserAuth.objects.get_or_create(email=email, username=email, login_type=LoginType.microsoft)

        jwt_access_token = generate_jwt_token(user)
        jwt_refresh_token = generate_jwt_token(user, is_refresh=True)

        response = Response()
        response.data = {
            "id":user.user_id,
            "email": user.email,
            "username": user.username,
            "login_type": user.login_type,
            "access_token": jwt_access_token,
            "refresh_token": jwt_refresh_token,
        }
        response.set_cookie("jwt",jwt_access_token, httponly=True, secure=True, samesite="Lax")
        response.set_cookie("refresh_token",jwt_refresh_token, httponly=True, secure=True, samesite="Lax")
        response.status_code = 200
        return response