from rest_framework import serializers
from .models import UserNotifications, UserPreferences, UserPrivacy

class UserNotificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotifications
        fields = ['email_notifications', 'course_notifications', 'progress_notifications']

class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreferences
        fields = ['preferred_language', 'difficulty_level', 'daily_goal']

class UserPrivacySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPrivacy
        fields = ['profile_visibility', 'show_progress']

class PasswordChangeRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    def validate(self, data):
        user = self.context['user']
        if data['email'] != user.email:
            raise serializers.ValidationError("Email does not match the authenticated user")
        return data 