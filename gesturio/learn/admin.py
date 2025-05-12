from django.contrib import admin
from .models import Category, Lesson, UserLessonProgress, LessonSteps

class LessonStepsInline(admin.TabularInline):
    model = LessonSteps
    extra = 1
    fields = (
        ('step_number', 'sign_name'),
        ('image', 'video')
    )
    verbose_name = "Sign Step"
    verbose_name_plural = "Sign Steps"
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['step_number'].label = "Step Number (1, 2, 3...)"
        formset.form.base_fields['sign_name'].label = "Name of the Sign"
        formset.form.base_fields['image'].label = "Image URL (optional)"
        formset.form.base_fields['video'].label = "Video URL (optional)"
        return formset

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = (
        ('title', 'duration'),
        'description',
        'image'
    )
    verbose_name = "Lesson"
    verbose_name_plural = "Lessons"
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['title'].label = "Lesson Title"
        formset.form.base_fields['duration'].label = "Duration (in minutes)"
        formset.form.base_fields['description'].label = "Lesson Description"
        formset.form.base_fields['image'].label = "Lesson Image URL (optional)"
        return formset

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'slug', 'created_at', 'updated_at')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    list_per_page = 20
    inlines = [LessonInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'image'),
            'description': 'Enter the basic details about this category of sign language lessons.'
        }),
        ('Advanced Settings', {
            'fields': ('slug',),
            'classes': ('collapse',),
            'description': 'These settings are automatically generated but can be modified if needed.'
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['title'].label = "Category Title"
        form.base_fields['description'].label = "Category Description"
        form.base_fields['image'].label = "Category Image URL (optional)"
        form.base_fields['slug'].label = "URL Slug (auto-generated)"
        return form

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'duration', 'created_at', 'updated_at')
    search_fields = ('title',)
    list_filter = ('category', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    list_per_page = 20
    inlines = [LessonStepsInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'title', 'description', 'duration', 'image'),
            'description': 'Enter the details about this sign language lesson.'
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['category'].label = "Select Category"
        form.base_fields['title'].label = "Lesson Title"
        form.base_fields['description'].label = "Lesson Description"
        form.base_fields['duration'].label = "Duration (in minutes)"
        form.base_fields['image'].label = "Lesson Image URL (optional)"
        return form

@admin.register(UserLessonProgress)
class UserLessonProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_username', 'get_lesson_title', 'completed', 'last_accessed')
    search_fields = ('user__username', 'lesson__title')
    list_filter = ('completed', 'last_accessed')
    ordering = ('-last_accessed',)
    list_per_page = 20

    def get_username(self, obj):
        return obj.user.username if obj.user else '-'
    get_username.short_description = 'User'

    def get_lesson_title(self, obj):
        return obj.lesson.title if obj.lesson else '-'
    get_lesson_title.short_description = 'Lesson'

@admin.register(LessonSteps)
class LessonStepsAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_lesson_title', 'step_number', 'sign_name', 'created_at', 'updated_at')
    search_fields = ('lesson__title', 'sign_name')
    list_filter = ('lesson', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    list_per_page = 20
    
    fieldsets = (
        ('Step Information', {
            'fields': ('lesson', 'step_number', 'sign_name', 'image', 'video'),
            'description': 'Enter the details for this sign language step.'
        }),
    )
    
    def get_lesson_title(self, obj):
        return obj.lesson.title if obj.lesson else '-'
    get_lesson_title.short_description = 'Lesson'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['lesson'].label = "Select Lesson"
        form.base_fields['step_number'].label = "Step Number (1, 2, 3...)"
        form.base_fields['sign_name'].label = "Name of the Sign"
        form.base_fields['image'].label = "Image URL (optional)"
        form.base_fields['video'].label = "Video URL (optional)"
        return form