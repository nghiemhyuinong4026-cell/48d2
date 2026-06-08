from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from core.models import CapaAction, Notification


class Command(BaseCommand):
    help = 'Scan for overdue CAPA actions and create notifications'
    
    def handle(self, *args, **options):
        now = timezone.now()
        overdue_count = 0
        notification_count = 0
        
        overdue_actions = CapaAction.objects.filter(
            deadline__lt=now,
            status__in=['pending', 'in_progress', 'submitted']
        ).exclude(
            status__in=['verified', 'closed']
        ).select_related('responsible_person', 'issue')
        
        for action in overdue_actions:
            overdue_count += 1
            
            existing_notification = Notification.objects.filter(
                action=action,
                notification_type='overdue',
                created_at__date=now.date()
            ).exists()
            
            if not existing_notification:
                with transaction.atomic():
                    old_status = action.status
                    if old_status != 'overdue':
                        action.status = 'overdue'
                        action.save(update_fields=['status'])
                    
                    Notification.objects.create(
                        recipient=action.responsible_person,
                        action=action,
                        issue=action.issue,
                        notification_type='overdue',
                        title=f'整改任务已逾期: {action.action_no}',
                        message=(
                            f'您负责的整改任务 {action.action_no} 已于 {action.deadline} 逾期。\n'
                            f'当前状态: {action.get_status_display()}\n'
                            f'异常单: {action.issue.title}\n'
                            f'请尽快完成整改并提交证据。'
                        )
                    )
                    notification_count += 1
                    
                    self.stdout.write(
                        self.style.WARNING(
                            f'Created overdue notification for action {action.action_no} '
                            f'(responsible: {action.responsible_person.get_full_name()})'
                        )
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Scan complete. Found {overdue_count} overdue actions, '
                f'created {notification_count} new notifications.'
            )
        )
        
        return f'Scanned {overdue_count} overdue actions, created {notification_count} notifications'
