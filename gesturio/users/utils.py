import jwt
import datetime
from django.conf import settings
from django.http import JsonResponse
from typing import Any
from .password_utils import generate_hash
from django.core.cache import cache
from .models import UserAuth
import random
import hashlib
from django.core.mail import EmailMessage

def otp_set_and_gen(email):
    otp = random.randint(100000, 999999)
    hashed_otp = generate_hash(str(otp))
    cache.set(f"otp:{email}", hashed_otp, settings.OTP_TTL)
    return otp

def md5_hash(data):
    md5_hash = hashlib.md5(data.encode())  # Encode string to bytes and compute hash
    return md5_hash.hexdigest()

def generate_jwt_token(user, is_refresh=False):
    
    expiry_minutes = settings.REFRESH_TOKEN_EXPIRY if is_refresh else settings.ACCESS_TOKEN_EXPIRY
    expiry = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=expiry_minutes)
    payload = {
        "user_id": user.user_id,
        "email": user.email,
        "exp": expiry,
        "is_refresh": is_refresh
    }

    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token

def validate_token(token):
    """Validate JWT token and return payload if valid."""
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

class Autherize:
    """Authorization decorator with refresh token support."""
    

    def __call__(self, func):
        """
        Decorator method to authorize the function.
        """

        def wrapper(*args, **kwargs):
            request = args[1] 
            token = request.COOKIES.get('jwt')
            refresh_token = request.COOKIES.get('refresh_token')

            if not token:
                return JsonResponse({"message": "Authentication required"}, status=401)

            # Validate access token
            payload = validate_token(token)
            if payload:
                try:
                    user = UserAuth.objects.get(user_id=payload["user_id"])
                    kwargs["user"] = user
                    return func(*args, **kwargs)
                except UserAuth.DoesNotExist:
                    return JsonResponse({"message": "User not found"}, status=404)

            # Try refresh token
            if not refresh_token:
                return JsonResponse({"message": "Session expired"}, status=401)

            refresh_payload = validate_token(refresh_token)
            if not refresh_payload:
                return JsonResponse({"message": "Invalid refresh token"}, status=401)

            try:
                user = UserAuth.objects.get(user_id=refresh_payload["user_id"])
                new_access_token = generate_jwt_token(user)
                response = JsonResponse({"message": "Token refreshed"})
                response.set_cookie("jwt", new_access_token, httponly=True, secure=True, samesite="Lax")
                kwargs["user"] = user
                return func(*args, **kwargs)
            except UserAuth.DoesNotExist:
                return JsonResponse({"message": "User not found"}, status=404)

        return wrapper


def send_email(subject, message, to):
    email = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [to])
    email.send()


