# Generated migration to create default users

from django.db import migrations
from django.contrib.auth.models import User

def create_default_users(apps, schema_editor):
    """Create default admin and test users"""
    # Create admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@ereft.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("✅ Created admin user")
    
    # Create test user
    test_user, created = User.objects.get_or_create(
        username='test_user',
        defaults={
            'email': 'test@ereft.com',
            'first_name': 'Test',
            'last_name': 'User',
            'is_active': True
        }
    )
    if created:
        test_user.set_password('testpass123')
        test_user.save()
        print("✅ Created test user")

def reverse_create_default_users(apps, schema_editor):
    """Remove default users"""
    User.objects.filter(username__in=['admin', 'test_user']).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('listings', '0002_userprofile_failed_login_attempts_and_more'),
    ]

    operations = [
        migrations.RunPython(create_default_users, reverse_create_default_users),
    ]
