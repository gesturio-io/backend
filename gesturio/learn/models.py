from django.db import models
from django.utils.text import slugify
from users.models import UserAuth

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    image = models.URLField(blank=True, null=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class Lesson(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.IntegerField(help_text="Duration in minutes")
    image = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class LessonSteps(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='steps')
    step_number = models.IntegerField()
    sign_name = models.TextField()
    image = models.URLField(blank=True, null=True)
    video = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['step_number']

class UserLessonProgress(models.Model):
    user = models.ForeignKey(UserAuth, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'lesson')
