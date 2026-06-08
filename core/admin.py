from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import (
    QualityIssue, CapaAction, EvidenceFile,
    Notification, AuditLog
)

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'role', 'phone', 'department')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)


@admin.register(QualityIssue)
class QualityIssueAdmin(admin.ModelAdmin):
    list_display = ('issue_no', 'title', 'status', 'severity', 'reporter', 'created_at')
    list_filter = ('status', 'severity')
    search_fields = ('issue_no', 'title', 'description')
    readonly_fields = ('issue_no', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'


@admin.register(CapaAction)
class CapaActionAdmin(admin.ModelAdmin):
    list_display = ('action_no', 'issue', 'status', 'responsible_person', 'deadline', 'created_at')
    list_filter = ('status',)
    search_fields = ('action_no', 'action_description')
    readonly_fields = ('action_no', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'


@admin.register(EvidenceFile)
class EvidenceFileAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'action', 'uploaded_by', 'uploaded_at')
    list_filter = ('file_type',)
    search_fields = ('file_name', 'description')
    readonly_fields = ('uploaded_at',)
    date_hierarchy = 'uploaded_at'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipient', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('title', 'message')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'model_name', 'object_repr', 'user', 'created_at')
    list_filter = ('action', 'model_name')
    search_fields = ('object_repr', 'details')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
