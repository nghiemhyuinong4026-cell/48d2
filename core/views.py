from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model

from .models import (
    QualityIssue, CapaAction, EvidenceFile,
    Notification, AuditLog
)
from .serializers import (
    QualityIssueSerializer, QualityIssueListSerializer,
    CapaActionSerializer, CapaActionListSerializer,
    SubmitEvidenceSerializer, VerifyActionSerializer,
    NotificationSerializer, AuditLogSerializer, EvidenceFileSerializer
)
from .state_machine import QualityIssueStateMachine, CapaActionStateMachine

User = get_user_model()


class QualityIssueViewSet(viewsets.ModelViewSet):
    queryset = QualityIssue.objects.select_related('reporter').all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return QualityIssueListSerializer
        return QualityIssueSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            issue = serializer.save(reporter=request.user)
            
            AuditLog.objects.create(
                user=request.user,
                action='create',
                model_name='QualityIssue',
                object_id=issue.id,
                object_repr=str(issue),
                new_values={
                    'title': issue.title,
                    'description': issue.description,
                    'status': issue.status
                },
                details=f'Created quality issue: {issue.issue_no}'
            )
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CapaActionViewSet(viewsets.ModelViewSet):
    queryset = CapaAction.objects.select_related(
        'issue', 'responsible_person', 'verified_by'
    ).prefetch_related('evidence_files').all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CapaActionListSerializer
        return CapaActionSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get('status')
        issue_id = self.request.query_params.get('issue')
        
        if status:
            queryset = queryset.filter(status=status)
        if issue_id:
            queryset = queryset.filter(issue_id=issue_id)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        issue_id = request.data.get('issue')
        responsible_person_id = request.data.get('responsible_person')
        
        try:
            issue = QualityIssue.objects.get(id=issue_id)
        except QualityIssue.DoesNotExist:
            return Response(
                {'error': 'Quality issue not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            responsible_person = User.objects.get(id=responsible_person_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Responsible person not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        with transaction.atomic():
            if issue.status == 'opened':
                QualityIssueStateMachine.transition(
                    issue, 'action_assigned', request.user,
                    details=f'Assigned CAPA action to {responsible_person.get_full_name()}'
                )
            
            action = CapaAction.objects.create(
                issue=issue,
                action_description=request.data.get('action_description'),
                responsible_person=responsible_person,
                deadline=request.data.get('deadline'),
                status='pending'
            )
            
            Notification.objects.create(
                recipient=responsible_person,
                action=action,
                issue=issue,
                notification_type='task_assigned',
                title=f'新的整改任务已分配: {action.action_no}',
                message=f'您已被分配为整改任务 {action.action_no} 的责任人，请于 {action.deadline} 前完成。'
            )
            
            AuditLog.objects.create(
                user=request.user,
                action='create',
                model_name='CapaAction',
                object_id=action.id,
                object_repr=str(action),
                new_values={
                    'action_description': action.action_description,
                    'responsible_person': responsible_person_id,
                    'deadline': str(action.deadline)
                },
                details=f'Created CAPA action: {action.action_no} for issue {issue.issue_no}'
            )
        
        serializer = self.get_serializer(action)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], url_path='submit-evidence')
    def submit_evidence(self, request, pk=None):
        action = self.get_object()
        
        if action.responsible_person != request.user:
            return Response(
                {'error': 'Only the responsible person can submit evidence'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if action.status == 'overdue':
            if not CapaActionStateMachine.can_transition('overdue', 'submitted'):
                pass
        elif not CapaActionStateMachine.can_transition(action.status, 'submitted'):
            return Response(
                {'error': f'Cannot submit evidence from status {action.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = SubmitEvidenceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            action.completion_description = serializer.validated_data['completion_description']
            action.actual_completed_at = timezone.now()
            
            files_data = serializer.validated_data.get('files', [])
            for file_data in files_data:
                EvidenceFile.objects.create(
                    action=action,
                    uploaded_by=request.user,
                    file_name=file_data.get('file_name', ''),
                    mock_url=file_data.get('mock_url', ''),
                    sha256=file_data.get('sha256', ''),
                    file_size=int(file_data.get('file_size', 0)),
                    file_type=file_data.get('file_type'),
                    description=file_data.get('description')
                )
            
            CapaActionStateMachine.transition(
                action, 'submitted', request.user,
                details=f'Evidence submitted by {request.user.get_full_name()}'
            )
            
            issue = action.issue
            if QualityIssueStateMachine.can_transition(issue.status, 'evidence_submitted'):
                QualityIssueStateMachine.transition(
                    issue, 'evidence_submitted', request.user,
                    details=f'Evidence submitted for action {action.action_no}'
                )
        
        return Response(self.get_serializer(action).data)
    
    @action(detail=True, methods=['post'], url_path='verify')
    def verify(self, request, pk=None):
        action = self.get_object()
        
        if request.user.role not in ['qa', 'quality_engineer']:
            return Response(
                {'error': 'Only QA or Quality Engineer can verify actions'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not CapaActionStateMachine.can_transition(action.status, 'verified'):
            return Response(
                {'error': f'Cannot verify action from status {action.status}. Evidence must be submitted first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not action.evidence_files.exists():
            return Response(
                {'error': 'Cannot verify action without evidence files'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = VerifyActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            action.verification_result = serializer.validated_data['verification_result']
            action.verified_by = request.user
            action.verified_at = timezone.now()
            
            if serializer.validated_data['approved']:
                CapaActionStateMachine.transition(
                    action, 'verified', request.user,
                    details=f'Verified and approved by {request.user.get_full_name()}'
                )
                
                issue = action.issue
                if QualityIssueStateMachine.can_transition(issue.status, 'verified'):
                    QualityIssueStateMachine.transition(
                        issue, 'verified', request.user,
                        details=f'Action {action.action_no} verified, issue ready to close'
                    )
                
                if QualityIssueStateMachine.can_transition(issue.status, 'closed'):
                    QualityIssueStateMachine.transition(
                        issue, 'closed', request.user,
                        details=f'Issue closed after successful verification'
                    )
                    CapaActionStateMachine.transition(
                        action, 'closed', request.user,
                        details=f'Action closed with issue'
                    )
            else:
                if CapaActionStateMachine.can_transition(action.status, 'in_progress'):
                    CapaActionStateMachine.transition(
                        action, 'in_progress', request.user,
                        details=f'Rejected by {request.user.get_full_name()}, sent back for rework'
                    )
                
                issue = action.issue
                if QualityIssueStateMachine.can_transition(issue.status, 'rejected'):
                    QualityIssueStateMachine.transition(
                        issue, 'rejected', request.user,
                        details=f'Action {action.action_no} rejected, issue sent back'
                    )
        
        return Response(self.get_serializer(action).data)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Notification.objects.filter(recipient=self.request.user)
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        return queryset
    
    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        if notification.recipient != request.user:
            return Response(
                {'error': 'Not allowed'},
                status=status.HTTP_403_FORBIDDEN
            )
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        return Response(self.get_serializer(notification).data)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = AuditLog.objects.select_related('user').all()
        model_name = self.request.query_params.get('model_name')
        user_id = self.request.query_params.get('user_id')
        action = self.request.query_params.get('action')
        
        if model_name:
            queryset = queryset.filter(model_name=model_name)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if action:
            queryset = queryset.filter(action=action)
        
        return queryset


class ScanOverdueViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=False, methods=['post'], url_path='run')
    def run_scan(self, request):
        from django.core.management import call_command
        from io import StringIO
        
        out = StringIO()
        call_command('scan_overdue', stdout=out)
        result = out.getvalue()
        
        return Response({
            'message': 'Overdue scan completed',
            'result': result
        })
    
    @action(detail=False, methods=['get'], url_path='info')
    def get_info(self, request):
        return Response({
            'command': 'scan_overdue',
            'description': 'Scan for overdue CAPA actions and create notifications',
            'usage': 'python manage.py scan_overdue',
            'functionality': 'Finds all CAPA actions where deadline has passed and status is not verified/closed. Creates overdue notifications for the responsible persons.'
        })
