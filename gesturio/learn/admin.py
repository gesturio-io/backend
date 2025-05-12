from django.contrib import admin
from .models import Category, Lesson, UserLessonProgress, LessonSteps
# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'slug', 'created_at', 'updated_at')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    list_per_page = 20
    
@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'duration', 'created_at', 'updated_at')
    search_fields = ('title',)
    list_filter = ('category', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    list_per_page = 20
    
@admin.register(UserLessonProgress)
class UserLessonProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'lesson', 'completed', 'last_accessed')
    search_fields = ('user__username', 'lesson__title')
    list_filter = ('completed', 'last_accessed')
    ordering = ('-last_accessed',)
    list_per_page = 20

@admin.register(LessonSteps)
class LessonStepsAdmin(admin.ModelAdmin):
    list_display = ('id', 'lesson', 'step_number', 'sign_name', 'created_at', 'updated_at')
    search_fields = ('lesson__title', 'sign_name')
    list_filter = ('lesson', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    list_per_page = 20