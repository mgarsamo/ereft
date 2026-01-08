"""
Management command to send a test welcome email to melaku.garsamo@gmail.com
Usage: python manage.py test_welcome_email
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from listings.utils import send_welcome_email


class Command(BaseCommand):
    help = 'Send a test welcome email to melaku.garsamo@gmail.com'

    def handle(self, *args, **options):
        try:
            # Get test user - handle case where multiple users might have the same email
            test_email = 'admin@ereft.com'
            test_user = User.objects.filter(email=test_email).first()
            
            if not test_user:
                # Create new user if none exists
                test_user = User.objects.create_user(
                    username='admin_test',
                    email=test_email,
                    first_name='Admin',
                    last_name='Test',
                    password='testpassword123'
                )
                self.stdout.write(f'✅ Created test user: {test_user.email}')
            else:
                self.stdout.write(f'✅ Using existing user: {test_user.email} (ID: {test_user.id})')
            
            self.stdout.write(self.style.SUCCESS(f'📧 Sending test welcome email to {test_user.email}...'))
            
            # Send test welcome email
            result = send_welcome_email(test_user, is_new_user=True, test_email='admin@ereft.com')
            
            if result:
                self.stdout.write(self.style.SUCCESS('✅ Test welcome email sent successfully!'))
            else:
                self.stdout.write(self.style.ERROR('❌ Failed to send test welcome email'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))
            import traceback
            traceback.print_exc()

