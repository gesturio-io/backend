from django.contrib import admin
from .models import SignSection, Sign

@admin.register(SignSection)
class SignSectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

@admin.register(Sign)
class SignAdmin(admin.ModelAdmin):
    list_display = ('name', 'section', 'difficulty', 'language', 'is_active')
    list_filter = ('difficulty', 'language', 'is_active', 'section')
    search_fields = ('name', 'description', 'language')
    list_editable = ('is_active',)
