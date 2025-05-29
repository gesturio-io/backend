from django.db import models
from users.models import UserAuth

# Create your models here.

class UserNotifications(models.Model):
    user = models.OneToOneField(UserAuth, on_delete=models.CASCADE, related_name='notifications')
    email_notifications = models.BooleanField(default=True)
    course_notifications = models.BooleanField(default=True)
    progress_notifications = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notifications for {self.user.email}"

class UserPreferences(models.Model):
    user = models.OneToOneField(UserAuth, on_delete=models.CASCADE, related_name='preferences')
    preferred_language = models.CharField(max_length=50, default='en')
    difficulty_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ], default='beginner')
    daily_goal = models.IntegerField(default=30)  # in minutes
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences for {self.user.email}"

class UserPrivacy(models.Model):
    user = models.OneToOneField(UserAuth, on_delete=models.CASCADE, related_name='privacy')
    profile_visibility = models.CharField(max_length=20, choices=[
        ('public', 'Public'),
        ('friends', 'Friends Only'),
        ('private', 'Private')
    ], default='public')
    show_progress = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Privacy settings for {self.user.email}"
