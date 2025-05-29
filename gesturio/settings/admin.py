from django.contrib import admin
from django.utils.html import format_html
from .models import UserNotifications, UserPreferences, UserPrivacy

@admin.register(UserNotifications)
class UserNotificationsAdmin(admin.ModelAdmin):
    list_display = ('get_user_info', 'get_notification_status', 'get_last_updated')
    list_filter = ('email_notifications', 'course_notifications', 'progress_notifications')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',),
            'description': 'User associated with these notification settings.'
        }),
        ('Notification Preferences', {
            'fields': (
                'email_notifications',
                'course_notifications',
                'progress_notifications'
            ),
            'description': 'Configure which notifications the user will receive.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'Record of when these settings were created and last modified.'
        }),
    )

    def get_user_info(self, obj):
        return format_html(
            '<div style="line-height: 1.5;">'
            '<strong>{}</strong><br/>'
            '<small style="color: #666;">{}</small>'
            '</div>',
            f"{obj.user.profile.firstname} {obj.user.profile.lastname}",
            obj.user.email
        )
    get_user_info.short_description = 'User'

    def get_notification_status(self, obj):
        status = []
        if obj.email_notifications:
            status.append('Email')
        if obj.course_notifications:
            status.append('Course')
        if obj.progress_notifications:
            status.append('Progress')
        return format_html(
            '<span style="color: #1a73e8;">{}</span>',
            ', '.join(status) if status else 'None'
        )
    get_notification_status.short_description = 'Active Notifications'

    def get_last_updated(self, obj):
        return format_html(
            '<span style="color: #666;">{}</span>',
            obj.updated_at.strftime('%Y-%m-%d %H:%M')
        )
    get_last_updated.short_description = 'Last Updated'

@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ('get_user_info', 'get_preferences_summary', 'get_last_updated')
    list_filter = ('difficulty_level', 'preferred_language')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',),
            'description': 'User associated with these preferences.'
        }),
        ('Learning Preferences', {
            'fields': (
                'preferred_language',
                'difficulty_level',
                'daily_goal'
            ),
            'description': 'Configure user learning preferences and goals.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'Record of when these preferences were created and last modified.'
        }),
    )

    def get_user_info(self, obj):
        return format_html(
            '<div style="line-height: 1.5;">'
            '<strong>{}</strong><br/>'
            '<small style="color: #666;">{}</small>'
            '</div>',
            f"{obj.user.profile.firstname} {obj.user.profile.lastname}",
            obj.user.email
        )
    get_user_info.short_description = 'User'

    def get_preferences_summary(self, obj):
        return format_html(
            '<div style="line-height: 1.5;">'
            '<span style="color: #1a73e8;">{}</span><br/>'
            '<small style="color: #666;">{}</small>'
            '</div>',
            f"{obj.difficulty_level.title()} Level",
            f"{obj.daily_goal} min daily goal"
        )
    get_preferences_summary.short_description = 'Preferences'

    def get_last_updated(self, obj):
        return format_html(
            '<span style="color: #666;">{}</span>',
            obj.updated_at.strftime('%Y-%m-%d %H:%M')
        )
    get_last_updated.short_description = 'Last Updated'

@admin.register(UserPrivacy)
class UserPrivacyAdmin(admin.ModelAdmin):
    list_display = ('get_user_info', 'get_privacy_status', 'get_last_updated')
    list_filter = ('profile_visibility', 'show_progress')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',),
            'description': 'User associated with these privacy settings.'
        }),
        ('Privacy Settings', {
            'fields': (
                'profile_visibility',
                'show_progress'
            ),
            'description': 'Configure user privacy preferences.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'Record of when these privacy settings were created and last modified.'
        }),
    )

    def get_user_info(self, obj):
        return format_html(
            '<div style="line-height: 1.5;">'
            '<strong>{}</strong><br/>'
            '<small style="color: #666;">{}</small>'
            '</div>',
            f"{obj.user.profile.firstname} {obj.user.profile.lastname}",
            obj.user.email
        )
    get_user_info.short_description = 'User'

    def get_privacy_status(self, obj):
        return format_html(
            '<div style="line-height: 1.5;">'
            '<span style="color: #1a73e8;">{}</span><br/>'
            '<small style="color: #666;">{}</small>'
            '</div>',
            obj.profile_visibility.title(),
            'Progress Visible' if obj.show_progress else 'Progress Hidden'
        )
    get_privacy_status.short_description = 'Privacy Status'

    def get_last_updated(self, obj):
        return format_html(
            '<span style="color: #666;">{}</span>',
            obj.updated_at.strftime('%Y-%m-%d %H:%M')
        )
    get_last_updated.short_description = 'Last Updated'
