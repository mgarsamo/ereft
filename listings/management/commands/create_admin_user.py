from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from listings.models import UserProfile

class Command(BaseCommand):
    help = 'Create admin user and demo users for testing'

    def handle(self, *args, **options):
        self.stdout.write('🔑 Creating admin and demo users...')
        
        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@ereft.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_active': True,
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write('✅ Created admin user: admin / admin123')
        else:
            # Update password in case it changed
            admin_user.set_password('admin123')
            admin_user.is_active = True
            admin_user.save()
            self.stdout.write('✅ Updated admin user: admin / admin123')
        
        # Create or update UserProfile for admin (with email_verified=True for demo)
        admin_profile, profile_created = UserProfile.objects.get_or_create(
            user=admin_user,
            defaults={
                'phone_number': '+251911000000',
                'is_agent': True,
                'email_verified': True,  # Skip email verification for admin
                'is_locked': False,
                'failed_login_attempts': 0
            }
        )
        
        if not profile_created:
            # Update existing profile
            admin_profile.email_verified = True
            admin_profile.is_locked = False
            admin_profile.failed_login_attempts = 0
            admin_profile.save()
        
        # Create test user (from original populate command)
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
            self.stdout.write('✅ Created test user: test_user / testpass123')
        else:
            test_user.set_password('testpass123')
            test_user.is_active = True
            test_user.save()
            self.stdout.write('✅ Updated test user: test_user / testpass123')
        
        # Create or update UserProfile for test user
        test_profile, profile_created = UserProfile.objects.get_or_create(
            user=test_user,
            defaults={
                'phone_number': '+251911000001',
                'is_agent': False,
                'email_verified': True,  # Skip email verification for demo
                'is_locked': False,
                'failed_login_attempts': 0
            }
        )
        
        if not profile_created:
            test_profile.email_verified = True
            test_profile.is_locked = False
            test_profile.failed_login_attempts = 0
            test_profile.save()
        
        self.stdout.write('🎉 Admin and demo users ready!')
        self.stdout.write('📋 Available demo credentials:')
        self.stdout.write('   👑 Admin: admin / admin123 (superuser)')
        self.stdout.write('   👤 Test: test_user / testpass123 (regular user)')
        self.stdout.write('   ✅ Both users have email_verified=True for immediate login')
