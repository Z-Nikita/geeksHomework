from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, TaskLog


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('id', 'email', 'first_name', 'last_name', 'phone_number', 'birthdate', 'registration_source', 'is_staff', 'is_active', 'is_superuser')
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    ordering = ('id',)
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number', 'birthdate', 'registration_source')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone_number', 'birthdate', 'registration_source', 'password1', 'password2', 'is_staff', 'is_active', 'is_superuser')
        }),
    )


@admin.register(TaskLog)
class TaskLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'task_type', 'recipient_email', 'status', 'created_at')
    list_filter = ('task_type', 'status', 'created_at')
    search_fields = ('message', 'recipient_email')
    ordering = ('-created_at',)
