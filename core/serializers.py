from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    QualityIssue, CapaAction, EvidenceFile, 
    Notification, AuditLog
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'phone', 'department']
        read_only_fields = ['id', 'email']


class EvidenceFileSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    
    class Meta:
        model = EvidenceFile
        fields = [
            'id', 'action', 'uploaded_by', 'file_name', 
            'mock_url', 'sha256', 'file_size', 'file_type',
            'description', 'uploaded_at'
        ]
        read_only_fields = ['id', 'uploaded_by', 'uploaded_at']


class QualityIssueListSerializer(serializers.ModelSerializer):
    reporter = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    
    class Meta:
        model = QualityIssue
        fields = [
            'id', 'issue_no', 'title', 'description', 'severity', 
            'severity_display', 'product_name', 'batch_no', 'discovered_at',
            'reporter', 'status', 'status_display', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'issue_no', 'created_at', 'updated_at']


class QualityIssueSerializer(serializers.ModelSerializer):
    reporter = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    
    class Meta:
        model = QualityIssue
        fields = [
            'id', 'issue_no', 'title', 'description', 'severity', 
            'severity_display', 'product_name', 'batch_no', 'discovered_at',
            'reporter', 'status', 'status_display', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'issue_no', 'status', 'created_at', 'updated_at']


class CapaActionListSerializer(serializers.ModelSerializer):
    responsible_person = UserSerializer(read_only=True)
    verified_by = UserSerializer(read_only=True)
    issue_title = serializers.CharField(source='issue.title', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = CapaAction
        fields = [
            'id', 'action_no', 'issue', 'issue_title', 'action_description',
            'responsible_person', 'deadline', 'status', 'status_display',
            'is_overdue', 'actual_completed_at', 'created_at', 'updated_at'
        ]


class CapaActionSerializer(serializers.ModelSerializer):
    responsible_person = UserSerializer(read_only=True)
    verified_by = UserSerializer(read_only=True)
    issue = serializers.PrimaryKeyRelatedField(queryset=QualityIssue.objects.all())
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    evidence_files = EvidenceFileSerializer(many=True, read_only=True, source='evidence_files')
    
    class Meta:
        model = CapaAction
        fields = [
            'id', 'action_no', 'issue', 'action_description',
            'responsible_person', 'deadline', 'status', 'status_display',
            'is_overdue', 'actual_completed_at', 'completion_description',
            'verification_result', 'verified_by', 'verified_at',
            'evidence_files', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'action_no', 'status', 'actual_completed_at', 
            'completion_description', 'verification_result', 'verified_by',
            'verified_at', 'created_at', 'updated_at', 'is_overdue'
        ]


class SubmitEvidenceSerializer(serializers.Serializer):
    completion_description = serializers.CharField(required=True)
    files = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        ),
        required=False,
        default=list
    )


class VerifyActionSerializer(serializers.Serializer):
    verification_result = serializers.CharField(required=True)
    approved = serializers.BooleanField(required=True)


class NotificationSerializer(serializers.ModelSerializer):
    recipient = UserSerializer(read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'notification_type', 'title',
            'message', 'is_read', 'read_at', 'created_at',
            'action', 'issue'
        ]
        read_only_fields = ['id', 'created_at']


class AuditLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'action', 'model_name', 'object_id',
            'object_repr', 'old_values', 'new_values', 'details',
            'ip_address', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
