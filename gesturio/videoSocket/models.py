from django.db import models
from users.models import UserAuth

# Create your models here.

class VideoSession(models.Model):
    room_name = models.CharField(max_length=255, unique=True)
    host = models.ForeignKey(UserAuth, on_delete=models.CASCADE, related_name='hosted_sessions')
    participants = models.ManyToManyField(UserAuth, related_name='participated_sessions')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Video Session: {self.room_name}"
