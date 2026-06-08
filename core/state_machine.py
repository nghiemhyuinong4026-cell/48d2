from django.utils import timezone
from django.db import transaction
from .models import QualityIssue, CapaAction, AuditLog, Notification


class QualityIssueStateMachine:
    VALID_TRANSITIONS = {
        'opened': ['action_assigned'],
        'action_assigned': ['evidence_submitted', 'rejected'],
        'evidence_submitted': ['verified', 'rejected'],
        'verified': ['closed'],
        'rejected': ['action_assigned'],
        'closed': [],
    }
    
    @classmethod
    def can_transition(cls, current_status, target_status):
        return target_status in cls.VALID_TRANSITIONS.get(current_status, [])
    
    @classmethod
    @transaction.atomic
    def transition(cls, issue, target_status, user, reason=None, details=None):
        if not cls.can_transition(issue.status, target_status):
            raise ValueError(
                f'Cannot transition issue from {issue.status} to {target_status}'
            )
        
        old_status = issue.status
        issue.status = target_status
        issue.save()
        
        AuditLog.objects.create(
            user=user,
            action='status_change',
            model_name='QualityIssue',
            object_id=issue.id,
            object_repr=str(issue),
            old_values={'status': old_status},
            new_values={'status': target_status},
            details=details or f'Status changed from {old_status} to {target_status}'
        )
        
        return issue


class CapaActionStateMachine:
    VALID_TRANSITIONS = {
        'pending': ['in_progress', 'overdue'],
        'in_progress': ['submitted', 'overdue'],
        'submitted': ['verified', 'overdue'],
        'verified': ['closed'],
        'closed': [],
        'overdue': ['in_progress', 'submitted'],
    }
    
    @classmethod
    def can_transition(cls, current_status, target_status):
        return target_status in cls.VALID_TRANSITIONS.get(current_status, [])
    
    @classmethod
    @transaction.atomic
    def transition(cls, action, target_status, user, reason=None, details=None):
        if not cls.can_transition(action.status, target_status):
            raise ValueError(
                f'Cannot transition action from {action.status} to {target_status}'
            )
        
        old_status = action.status
        action.status = target_status
        action.save()
        
        if action.responsible_person:
            Notification.objects.create(
                recipient=action.responsible_person,
                action=action,
                issue=action.issue,
                notification_type='status_update',
                title=f'整改任务状态更新: {action.action_no}',
                message=f'您负责的整改任务 {action.action_no} 状态已从 {old_status} 变更为 {target_status}'
            )
        
        AuditLog.objects.create(
            user=user,
            action='status_change',
            model_name='CapaAction',
            object_id=action.id,
            object_repr=str(action),
            old_values={'status': old_status},
            new_values={'status': target_status},
            details=details or f'Status changed from {old_status} to {target_status}'
        )
        
        return action
