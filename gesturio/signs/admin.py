from django.contrib import admin
from .models import SignSection, Sign

@admin.register(SignSection)
class SignSectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'sign_count')
    search_fields = ('name', 'description')

    def sign_count(self, obj):
        return obj.sign_set.count()
    sign_count.short_description = 'Number of Signs'

@admin.register(Sign)
class SignAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_section_name', 'difficulty', 'language', 'is_active')
    list_filter = ('difficulty', 'language', 'is_active', 'section')
    search_fields = ('name', 'description', 'language')
    list_editable = ('is_active',)

    def get_section_name(self, obj):
        return obj.section.name if obj.section else '-'
    get_section_name.short_description = 'Section'
