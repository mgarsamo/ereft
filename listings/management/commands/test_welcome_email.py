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
            # Get or create a test user
            test_user, created = User.objects.get_or_create(
                email='melaku.garsamo@gmail.com',
                defaults={
                    'username': 'test_user',
                    'first_name': 'Melaku',
                    'is_active': True,
                }
            )
            
            if not test_user.first_name:
                test_user.first_name = 'Melaku'
                test_user.save()
            
            self.stdout.write(self.style.SUCCESS(f'📧 Sending test welcome email to {test_user.email}...'))
            
            # Send test welcome email
            result = send_welcome_email(test_user, is_new_user=True, test_email='melaku.garsamo@gmail.com')
            
            if result:
                self.stdout.write(self.style.SUCCESS('✅ Test welcome email sent successfully!'))
            else:
                self.stdout.write(self.style.ERROR('❌ Failed to send test welcome email'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))
            import traceback
            traceback.print_exc()

