from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from unfold.admin import ModelAdmin

User = get_user_model()


@admin.register(User)
class UserAdmin(ModelAdmin, BaseUserAdmin):
    list_display = ['email', 'full_name', 'is_business', 'is_staff', 'is_superuser', 'created_at']
    list_filter = ['is_business', 'is_staff', 'is_superuser']  # Removed is_active
    search_fields = ['email', 'full_name']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal', {'fields': ('full_name', 'profile_image')}),
        ('Permissions', {'fields': ('is_business', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'full_name', 'is_business', 'is_staff'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login']