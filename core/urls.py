from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    QualityIssueViewSet, CapaActionViewSet,
    NotificationViewSet, AuditLogViewSet,
    ScanOverdueViewSet
)

router = DefaultRouter()
router.register(r'quality-issues', QualityIssueViewSet, basename='quality-issue')
router.register(r'capa-actions', CapaActionViewSet, basename='capa-action')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')
router.register(r'scan-overdue', ScanOverdueViewSet, basename='scan-overdue')

urlpatterns = [
    path('', include(router.urls)),
]
