from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.admin import SimpleListFilter
from django.utils.safestring import mark_safe
from .models import UserAuth, UserProfile, LoginType, UserLoginLog, Friends

class EmailVerifiedFilter(SimpleListFilter):
    title = 'Email Verification Status'
    parameter_name = 'email_verified'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Verified'),
            ('no', 'Not Verified'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(email_verified=True)
        if self.value() == 'no':
            return queryset.filter(email_verified=False)
        return queryset

class LoginTypeFilter(SimpleListFilter):
    title = 'Login Type'
    parameter_name = 'login_type'

    def lookups(self, request, model_admin):
        return [(lt.value, lt.name.title()) for lt in LoginType]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(login_type=self.value())
        return queryset

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    fields = (
        ('firstname', 'lastname'),
        'profile_picture',
        'bio',
        ('country', 'native_language'),
        ('gender', 'date_of_birth'),
        ('is_premium', 'daily_goal'),
        ('phone_number', 'requirement'),
    )
    readonly_fields = ('user', 'get_profile_picture_preview')
    extra = 0
    
    def get_profile_picture_preview(self, obj):
        if obj.profile_picture:
            return mark_safe(f'<img src="{obj.profile_picture}" style="max-height: 150px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />')
        return "No picture uploaded"
    get_profile_picture_preview.short_description = 'Profile Picture Preview'

@admin.register(UserAuth)
class UserAuthAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'get_login_type_badge', 'get_verification_status', 'is_active', 'created_at', 'last_active', 'get_profile_link')
    list_filter = (EmailVerifiedFilter, LoginTypeFilter, 'is_active', 'created_at')
    search_fields = ('username', 'email')
    readonly_fields = ('created_at', 'last_active', 'get_last_login_display')
    ordering = ('-created_at',)
    inlines = [UserProfileInline]
    list_per_page = 20
    save_on_top = True
    
    fieldsets = (
        ('Authentication', {
            'fields': ('username', 'email', 'password', 'login_type'),
            'classes': ('wide',),
            'description': 'Basic authentication information for the user.'
        }),
        ('Status', {
            'fields': ('email_verified', 'is_active', 'get_last_login_display'),
            'classes': ('wide',),
            'description': 'User account status and verification information.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_active'),
            'classes': ('collapse',),
            'description': 'Account creation and activity timestamps.'
        }),
    )

    def get_login_type_badge(self, obj):
        colors = {
            'email': '#28a745',
            'google': '#dc3545',
            'microsoft': '#007bff'
        }
        return mark_safe(f'<span style="background-color: {colors[obj.login_type]}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.8em;">{obj.login_type.title()}</span>')
    get_login_type_badge.short_description = 'Login Type'

    def get_verification_status(self, obj):
        if obj.email_verified:
            return mark_safe('<span style="color: #28a745;"><b>✓</b> Verified</span>')
        return mark_safe('<span style="color: #dc3545;"><b>×</b> Not Verified</span>')
    get_verification_status.short_description = 'Verification'

    def get_last_login_display(self, obj):
        return format_html('<span style="color: #666;">{}</span>', obj.last_active.strftime("%Y-%m-%d %H:%M:%S"))
    get_last_login_display.short_description = 'Last Login'

    def get_profile_link(self, obj):
        if hasattr(obj, 'profile'):
            url = reverse('admin:users_userprofile_change', args=[obj.profile.id])
            return format_html('<a class="button" style="background-color: #007bff; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none;" href="{}">View Profile</a>', url)
        return '-'
    get_profile_link.short_description = 'Profile'

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('get_user_info', 'get_location', 'get_premium_status', 'daily_goal', 'get_requirement_badge')
    list_filter = ('is_premium', 'requirement', 'country')
    search_fields = ('user__username', 'user__email', 'firstname', 'lastname', 'country')
    readonly_fields = ('user', 'get_profile_picture_preview')
    list_per_page = 20
    save_on_top = True
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', ('firstname', 'lastname'), 'profile_picture', 'get_profile_picture_preview'),
            'classes': ('wide',),
            'description': 'Basic user profile information.'
        }),
        ('Personal Details', {
            'fields': ('bio', ('country', 'native_language'), ('gender', 'date_of_birth')),
            'classes': ('wide',),
            'description': 'Detailed personal information about the user.'
        }),
        ('Preferences', {
            'fields': (('is_premium', 'daily_goal'), ('phone_number', 'requirement')),
            'classes': ('wide',),
            'description': 'User preferences and account settings.'
        }),
    )

    def get_user_info(self, obj):
        return format_html(
            '<div style="line-height: 1.5;">'
            '<strong>{}</strong><br/>'
            '<small style="color: #666;">{}</small>'
            '</div>',
            f"{obj.firstname} {obj.lastname}",
            obj.user.email
        )
    get_user_info.short_description = 'User'

    def get_location(self, obj):
        if obj.country:
            return format_html('<span style="color: #1a73e8;">{}</span>', obj.country)
        return '-'
    get_location.short_description = 'Location'

    def get_premium_status(self, obj):
        if obj.is_premium:
            return mark_safe('<span style="background-color: #ffd700; color: #000; padding: 3px 8px; border-radius: 12px; font-size: 0.8em;">Premium</span>')
        return mark_safe('<span style="background-color: #e0e0e0; color: #666; padding: 3px 8px; border-radius: 12px; font-size: 0.8em;">Standard</span>')
    get_premium_status.short_description = 'Status'

    def get_requirement_badge(self, obj):
        colors = {
            'Other': '#6c757d',
            'Just for Fun': '#28a745',
            'Friends': '#17a2b8',
            'Family': '#ffc107',
            'Work': '#dc3545'
        }
        return mark_safe(f'<span style="background-color: {colors[obj.requirement]}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.8em;">{obj.requirement}</span>')
    get_requirement_badge.short_description = 'Requirement'

    def get_profile_picture_preview(self, obj):
        if obj.profile_picture:
            return mark_safe(f'<img src="{obj.profile_picture}" style="max-height: 200px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />')
        return "No picture uploaded"
    get_profile_picture_preview.short_description = 'Profile Picture Preview'

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }

@admin.register(UserLoginLog)
class UserLoginLogAdmin(admin.ModelAdmin):
    list_display = ('get_user_username', 'get_user_email', 'ip_address', 'visit_date', 'created_at')
    list_filter = ('visit_date',)
    search_fields = ('user_id__username', 'user_id__email', 'ip_address')
    readonly_fields = ('created_at',)

    def get_user_username(self, obj):
        return obj.user_id.username if obj.user_id else '-'
    get_user_username.short_description = 'Username'

    def get_user_email(self, obj):
        return obj.user_id.email if obj.user_id else '-'
    get_user_email.short_description = 'Email'

@admin.register(Friends)
class FriendsAdmin(admin.ModelAdmin):
    list_display = ('get_user_username', 'get_friend_username', 'status', 'created_at')
    list_filter = ('status',)
    readonly_fields = ('created_at',)

    def get_user_username(self, obj):
        return obj.user_id.username if obj.user_id else '-'
    get_user_username.short_description = 'User'

    def get_friend_username(self, obj):
        return obj.friend_id.username if obj.friend_id else '-'
    get_friend_username.short_description = 'Friend'
