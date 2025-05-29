from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.core.cache import cache
from users.utils import Autherize, otp_set_and_gen,send_email
from users.password_utils import generate_hash, verify_hash
from .models import UserNotifications, UserPreferences, UserPrivacy
from .serializers import UserNotificationsSerializer, UserPreferencesSerializer, UserPrivacySerializer,PasswordChangeRequestSerializer

class PasswordChangeView(APIView):
    @Autherize()
    def post(self, request, **kwargs):   # POST FOR REQUESTING OTP
        user = kwargs['user']
        serializer = PasswordChangeRequestSerializer(data=request.data,context={'user': user})
        email = serializer.data['email']
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        otp = otp_set_and_gen(email)
        cache_key = f'password_change_otp_{user.user_id}'
        cache.set(cache_key, otp, timeout=600)  # 10 minutes expiry
        
        send_email(
            subject="[noreply@gesturio.com] Your Gesturio Password Reset Code",
            msg=f'Your OTP for password change is: {otp}',
            to=email
        )
        
        return Response(
            {"message": "OTP sent to your email for verification"}, 
            status=status.HTTP_200_OK
        )

    @Autherize()
    def put(self, request, **kwargs): # POST FOR CHANGING PASSWORD
        user = kwargs['user']
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')
        
        if not otp or not new_password:
            return Response(
                {"error": "OTP and new password are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cache_key = f'password_change_otp_{user.user_id}'
        stored_otp = cache.get(cache_key)
        
        if not stored_otp or stored_otp != otp:
            return Response(
                {"error": "Invalid or expired OTP"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.password = generate_hash(new_password)
        user.save()
        
        cache.delete(cache_key)
        
        return Response(
            {"message": "Password changed successfully"}, 
            status=status.HTTP_200_OK
        )

class NotificationsView(APIView):
    @Autherize()
    def get(self, request, **kwargs):
        user = kwargs['user']
        notifications, created = UserNotifications.objects.get_or_create(user=user)
        serializer = UserNotificationsSerializer(notifications)
        return Response(serializer.data)

    @Autherize()
    def put(self, request, **kwargs):
        user = kwargs['user']
        notifications, created = UserNotifications.objects.get_or_create(user=user)
        serializer = UserNotificationsSerializer(notifications, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PreferencesView(APIView):
    @Autherize()
    def get(self, request, **kwargs):
        user = kwargs['user']
        preferences, created = UserPreferences.objects.get_or_create(user=user)
        serializer = UserPreferencesSerializer(preferences)
        return Response(serializer.data)

    @Autherize()
    def put(self, request, **kwargs):
        user = kwargs['user']
        preferences, created = UserPreferences.objects.get_or_create(user=user)
        serializer = UserPreferencesSerializer(preferences, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PrivacyView(APIView):
    @Autherize()
    def get(self, request, **kwargs):
        user = kwargs['user']
        privacy, created = UserPrivacy.objects.get_or_create(user=user)
        serializer = UserPrivacySerializer(privacy)
        return Response(serializer.data)

    @Autherize()
    def put(self, request, **kwargs):
        user = kwargs['user']
        privacy, created = UserPrivacy.objects.get_or_create(user=user)
        serializer = UserPrivacySerializer(privacy, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteAccountView(APIView):
    
    @Autherize()
    def get(self, request, **kwargs):
        user = kwargs['user']
        password = request.query_params.get('password')
        if not password:
            return Response(
                {"error": "Password is required to confirm account deletion"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        check = verify_hash(password, user.password)
        if not check:
            return Response(
                {"error": "Incorrect password"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {"message": "success"}, 
            status=status.HTTP_200_OK
        )
    
    @Autherize()
    def delete(self, request, **kwargs):
        user = kwargs['user']
        
        # Delete associated settings
        UserNotifications.objects.filter(user=user).delete()
        UserPreferences.objects.filter(user=user).delete()
        UserPrivacy.objects.filter(user=user).delete()
        
        # Delete user
        user.delete()
        
        return Response(
            {"message": "Account deleted successfully"}, 
            status=status.HTTP_200_OK
        )