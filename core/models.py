from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    ROLE_CHOICES = (
        ('quality_engineer', '质量工程师'),
        ('responsible_person', '责任人'),
        ('qa', 'QA'),
        ('auditor', '审计员'),
    )
    
    username = None
    email = models.EmailField('邮箱', unique=True)
    role = models.CharField('角色', max_length=30, choices=ROLE_CHOICES, default='responsible_person')
    phone = models.CharField('电话', max_length=20, blank=True, null=True)
    department = models.CharField('部门', max_length=100, blank=True, null=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户'
    
    def __str__(self):
        return f'{self.get_full_name()} ({self.get_role_display()})'


class QualityIssue(models.Model):
    STATUS_CHOICES = (
        ('opened', '已开启'),
        ('action_assigned', '整改中'),
        ('evidence_submitted', '证据已提交'),
        ('verified', '已验证'),
        ('closed', '已关闭'),
        ('rejected', '已驳回'),
    )
    
    SEVERITY_CHOICES = (
        ('critical', '严重'),
        ('major', '重要'),
        ('minor', '一般'),
    )
    
    issue_no = models.CharField('异常单号', max_length=50, unique=True)
    title = models.CharField('标题', max_length=200)
    description = models.TextField('详细描述')
    severity = models.CharField('严重程度', max_length=20, choices=SEVERITY_CHOICES, default='minor')
    product_name = models.CharField('产品名称', max_length=200, blank=True, null=True)
    batch_no = models.CharField('批次号', max_length=100, blank=True, null=True)
    discovered_at = models.DateTimeField('发现时间', default=timezone.now)
    discovered_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='discovered_issues', null=True, verbose_name='发现人')
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='reported_issues', null=True, verbose_name='报告人')
    status = models.CharField('状态', max_length=30, choices=STATUS_CHOICES, default='opened')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'quality_issues'
        verbose_name = '质量异常'
        verbose_name_plural = '质量异常'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.issue_no} - {self.title}'
    
    def save(self, *args, **kwargs):
        if not self.issue_no:
            today = timezone.now().strftime('%Y%m%d')
            count = QualityIssue.objects.filter(issue_no__startswith=f'QI-{today}-').count()
            self.issue_no = f'QI-{today}-{count + 1:04d}'
        super().save(*args, **kwargs)


class CapaAction(models.Model):
    STATUS_CHOICES = (
        ('pending', '待开始'),
        ('in_progress', '进行中'),
        ('submitted', '已提交'),
        ('verified', '已验证'),
        ('closed', '已关闭'),
        ('overdue', '已逾期'),
    )
    
    issue = models.ForeignKey(QualityIssue, on_delete=models.CASCADE, related_name='capa_actions', verbose_name='关联异常')
    action_no = models.CharField('整改单号', max_length=50, unique=True)
    action_description = models.TextField('整改措施描述')
    responsible_person = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='assigned_actions', null=True, verbose_name='责任人')
    deadline = models.DateTimeField('截止日期')
    status = models.CharField('状态', max_length=30, choices=STATUS_CHOICES, default='pending')
    actual_completed_at = models.DateTimeField('实际完成时间', blank=True, null=True)
    completion_description = models.TextField('完成说明', blank=True, null=True)
    verification_result = models.TextField('验证结果', blank=True, null=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='verified_actions', null=True, verbose_name='验证人')
    verified_at = models.DateTimeField('验证时间', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'capa_actions'
        verbose_name = 'CAPA整改措施'
        verbose_name_plural = 'CAPA整改措施'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.action_no} - {self.issue.title[:30]}'
    
    def save(self, *args, **kwargs):
        if not self.action_no:
            today = timezone.now().strftime('%Y%m%d')
            count = CapaAction.objects.filter(action_no__startswith=f'CA-{today}-').count()
            self.action_no = f'CA-{today}-{count + 1:04d}'
        super().save(*args, **kwargs)
    
    def is_overdue(self):
        return self.status not in ['verified', 'closed'] and timezone.now() > self.deadline


class EvidenceFile(models.Model):
    action = models.ForeignKey(CapaAction, on_delete=models.CASCADE, related_name='evidence_files', verbose_name='关联整改措施')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='uploaded_files', null=True, verbose_name='上传人')
    file_name = models.CharField('文件名', max_length=255)
    mock_url = models.CharField('模拟URL', max_length=500)
    sha256 = models.CharField('SHA256哈希', max_length=64)
    file_size = models.PositiveIntegerField('文件大小(字节)', default=0)
    file_type = models.CharField('文件类型', max_length=100, blank=True, null=True)
    description = models.TextField('文件描述', blank=True, null=True)
    uploaded_at = models.DateTimeField('上传时间', auto_now_add=True)
    
    class Meta:
        db_table = 'evidence_files'
        verbose_name = '证据文件'
        verbose_name_plural = '证据文件'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f'{self.file_name} ({self.action.action_no})'


class Notification(models.Model):
    TYPE_CHOICES = (
        ('overdue', '逾期提醒'),
        ('deadline_approaching', '即将到期'),
        ('task_assigned', '任务分配'),
        ('status_update', '状态更新'),
    )
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name='接收人')
    action = models.ForeignKey(CapaAction, on_delete=models.SET_NULL, related_name='notifications', null=True, blank=True, verbose_name='关联整改措施')
    issue = models.ForeignKey(QualityIssue, on_delete=models.SET_NULL, related_name='notifications', null=True, blank=True, verbose_name='关联异常')
    notification_type = models.CharField('通知类型', max_length=30, choices=TYPE_CHOICES)
    title = models.CharField('标题', max_length=200)
    message = models.TextField('消息内容')
    is_read = models.BooleanField('是否已读', default=False)
    read_at = models.DateTimeField('阅读时间', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        verbose_name = '通知'
        verbose_name_plural = '通知'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.get_notification_type_display()} - {self.recipient.get_full_name()}'


class AuditLog(models.Model):
    ACTION_CHOICES = (
        ('create', '创建'),
        ('update', '更新'),
        ('delete', '删除'),
        ('status_change', '状态变更'),
        ('login', '登录'),
        ('logout', '登出'),
    )
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='audit_logs', null=True, verbose_name='操作用户')
    action = models.CharField('操作类型', max_length=30, choices=ACTION_CHOICES)
    model_name = models.CharField('模型名称', max_length=100, blank=True, null=True)
    object_id = models.PositiveBigIntegerField('对象ID', blank=True, null=True)
    object_repr = models.CharField('对象表示', max_length=500, blank=True, null=True)
    old_values = models.JSONField('旧值', blank=True, null=True)
    new_values = models.JSONField('新值', blank=True, null=True)
    details = models.TextField('详细说明', blank=True, null=True)
    ip_address = models.CharField('IP地址', max_length=50, blank=True, null=True)
    user_agent = models.TextField('User Agent', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'audit_logs'
        verbose_name = '审计日志'
        verbose_name_plural = '审计日志'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.get_action_display()} by {self.user} at {self.created_at}'
