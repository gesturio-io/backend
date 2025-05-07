from django.db import models


class SignSection(models.Model):
    sign_section_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    icon_url = models.URLField(max_length=255)

    def __str__(self):
        return self.name


class Sign(models.Model):
    
    class Difficulty(models.TextChoices):   
        EASY = 'easy'
        MEDIUM = 'medium'
        HARD = 'hard'
    
    section = models.ForeignKey(SignSection, on_delete=models.CASCADE, related_name='signs')
    name = models.CharField(max_length=255)
    video_url = models.URLField(max_length=255)
    image_url = models.URLField(max_length=255)
    difficulty = models.CharField(max_length=50, choices=Difficulty.choices)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField()
    language = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} - {self.language}"

    class Meta:
        ordering = ['name'] 