from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed test users for CAPA system'
    
    def handle(self, *args, **options):
        test_users = [
            {
                'email': 'quality.engineer@example.com',
                'password': 'Test@1234',
                'first_name': '张工',
                'last_name': '质量工程师',
                'role': 'quality_engineer',
                'phone': '13800000001',
                'department': '质量部'
            },
            {
                'email': 'responsible.person@example.com',
                'password': 'Test@1234',
                'first_name': '李工',
                'last_name': '责任人',
                'role': 'responsible_person',
                'phone': '13800000002',
                'department': '生产部'
            },
            {
                'email': 'qa@example.com',
                'password': 'Test@1234',
                'first_name': '王工',
                'last_name': 'QA',
                'role': 'qa',
                'phone': '13800000003',
                'department': '质量保证部'
            },
            {
                'email': 'auditor@example.com',
                'password': 'Test@1234',
                'first_name': '赵工',
                'last_name': '审计员',
                'role': 'auditor',
                'phone': '13800000004',
                'department': '审计部'
            },
            {
                'email': 'admin@example.com',
                'password': 'Admin@1234',
                'first_name': '系统',
                'last_name': '管理员',
                'role': 'quality_engineer',
                'phone': '13800000000',
                'department': 'IT部',
                'is_staff': True,
                'is_superuser': True
            }
        ]
        
        created_count = 0
        skipped_count = 0
        
        for user_data in test_users:
            email = user_data.pop('email')
            password = user_data.pop('password')
            
            if User.objects.filter(email=email).exists():
                self.stdout.write(
                    self.style.WARNING(f'User {email} already exists, skipping')
                )
                skipped_count += 1
                continue
            
            User.objects.create_user(
                email=email,
                password=password,
                **user_data
            )
            created_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'Created user: {email}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Seed complete. Created {created_count} users, skipped {skipped_count} existing users.'
            )
        )
