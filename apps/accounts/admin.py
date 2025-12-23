from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile, APIKey


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name', 'tier', 'timezone', 'preferred_currency')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'tier'),
        }),
    )
    list_display = ('email', 'full_name', 'tier', 'is_staff', 'is_active')
    list_filter = ('tier', 'is_staff', 'is_active')
    search_fields = ('email', 'full_name')
    ordering = ('email',)
    readonly_fields = ('date_joined', 'last_login')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__email',)


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'key', 'created_at', 'is_active')
    search_fields = ('name', 'user__email')
    readonly_fields = ('key', 'created_at')