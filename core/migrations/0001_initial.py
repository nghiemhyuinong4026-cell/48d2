from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='邮箱')),
                ('role', models.CharField(choices=[('quality_engineer', '质量工程师'), ('responsible_person', '责任人'), ('qa', 'QA'), ('auditor', '审计员')], default='responsible_person', max_length=30, verbose_name='角色')),
                ('phone', models.CharField(blank=True, max_length=20, null=True, verbose_name='电话')),
                ('department', models.CharField(blank=True, max_length=100, null=True, verbose_name='部门')),
            ],
            options={
                'verbose_name': '用户',
                'verbose_name_plural': '用户',
                'db_table': 'users',
            },
        ),
        migrations.CreateModel(
            name='QualityIssue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('issue_no', models.CharField(max_length=50, unique=True, verbose_name='异常单号')),
                ('title', models.CharField(max_length=200, verbose_name='标题')),
                ('description', models.TextField(verbose_name='详细描述')),
                ('severity', models.CharField(choices=[('critical', '严重'), ('major', '重要'), ('minor', '一般')], default='minor', max_length=20, verbose_name='严重程度')),
                ('product_name', models.CharField(blank=True, max_length=200, null=True, verbose_name='产品名称')),
                ('batch_no', models.CharField(blank=True, max_length=100, null=True, verbose_name='批次号')),
                ('discovered_at', models.DateTimeField(default=timezone.now, verbose_name='发现时间')),
                ('status', models.CharField(choices=[('opened', '已开启'), ('action_assigned', '整改中'), ('evidence_submitted', '证据已提交'), ('verified', '已验证'), ('closed', '已关闭'), ('rejected', '已驳回')], default='opened', max_length=30, verbose_name='状态')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('discovered_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='discovered_issues', to='core.user', verbose_name='发现人')),
                ('reporter', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reported_issues', to='core.user', verbose_name='报告人')),
            ],
            options={
                'verbose_name': '质量异常',
                'verbose_name_plural': '质量异常',
                'db_table': 'quality_issues',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CapaAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_no', models.CharField(max_length=50, unique=True, verbose_name='整改单号')),
                ('action_description', models.TextField(verbose_name='整改措施描述')),
                ('deadline', models.DateTimeField(verbose_name='截止日期')),
                ('status', models.CharField(choices=[('pending', '待开始'), ('in_progress', '进行中'), ('submitted', '已提交'), ('verified', '已验证'), ('closed', '已关闭'), ('overdue', '已逾期')], default='pending', max_length=30, verbose_name='状态')),
                ('actual_completed_at', models.DateTimeField(blank=True, null=True, verbose_name='实际完成时间')),
                ('completion_description', models.TextField(blank=True, null=True, verbose_name='完成说明')),
                ('verification_result', models.TextField(blank=True, null=True, verbose_name='验证结果')),
                ('verified_at', models.DateTimeField(blank=True, null=True, verbose_name='验证时间')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('issue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='capa_actions', to='core.qualityissue', verbose_name='关联异常')),
                ('responsible_person', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_actions', to='core.user', verbose_name='责任人')),
                ('verified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='verified_actions', to='core.user', verbose_name='验证人')),
            ],
            options={
                'verbose_name': 'CAPA整改措施',
                'verbose_name_plural': 'CAPA整改措施',
                'db_table': 'capa_actions',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(choices=[('overdue', '逾期提醒'), ('deadline_approaching', '即将到期'), ('task_assigned', '任务分配'), ('status_update', '状态更新')], max_length=30, verbose_name='通知类型')),
                ('title', models.CharField(max_length=200, verbose_name='标题')),
                ('message', models.TextField(verbose_name='消息内容')),
                ('is_read', models.BooleanField(default=False, verbose_name='是否已读')),
                ('read_at', models.DateTimeField(blank=True, null=True, verbose_name='阅读时间')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('action', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notifications', to='core.capaaction', verbose_name='关联整改措施')),
                ('issue', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notifications', to='core.qualityissue', verbose_name='关联异常')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='core.user', verbose_name='接收人')),
            ],
            options={
                'verbose_name': '通知',
                'verbose_name_plural': '通知',
                'db_table': 'notifications',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='EvidenceFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(max_length=255, verbose_name='文件名')),
                ('mock_url', models.CharField(max_length=500, verbose_name='模拟URL')),
                ('sha256', models.CharField(max_length=64, verbose_name='SHA256哈希')),
                ('file_size', models.PositiveIntegerField(default=0, verbose_name='文件大小(字节)')),
                ('file_type', models.CharField(blank=True, max_length=100, null=True, verbose_name='文件类型')),
                ('description', models.TextField(blank=True, null=True, verbose_name='文件描述')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='上传时间')),
                ('action', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evidence_files', to='core.capaaction', verbose_name='关联整改措施')),
                ('uploaded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='uploaded_files', to='core.user', verbose_name='上传人')),
            ],
            options={
                'verbose_name': '证据文件',
                'verbose_name_plural': '证据文件',
                'db_table': 'evidence_files',
                'ordering': ['-uploaded_at'],
            },
        ),
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('create', '创建'), ('update', '更新'), ('delete', '删除'), ('status_change', '状态变更'), ('login', '登录'), ('logout', '登出')], max_length=30, verbose_name='操作类型')),
                ('model_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='模型名称')),
                ('object_id', models.PositiveBigIntegerField(blank=True, null=True, verbose_name='对象ID')),
                ('object_repr', models.CharField(blank=True, max_length=500, null=True, verbose_name='对象表示')),
                ('old_values', models.JSONField(blank=True, null=True, verbose_name='旧值')),
                ('new_values', models.JSONField(blank=True, null=True, verbose_name='新值')),
                ('details', models.TextField(blank=True, null=True, verbose_name='详细说明')),
                ('ip_address', models.CharField(blank=True, max_length=50, null=True, verbose_name='IP地址')),
                ('user_agent', models.TextField(blank=True, null=True, verbose_name='User Agent')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_logs', to='core.user', verbose_name='操作用户')),
            ],
            options={
                'verbose_name': '审计日志',
                'verbose_name_plural': '审计日志',
                'db_table': 'audit_logs',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
    ]
