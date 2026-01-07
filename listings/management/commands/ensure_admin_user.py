"""
Management command to ensure melaku.garsamo@gmail.com is set as admin
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from listings.models import UserProfile

class Command(BaseCommand):
    help = 'Ensure melaku.garsamo@gmail.com is set as admin user'

    def handle(self, *args, **options):
        email = 'melaku.garsamo@gmail.com'
        
        try:
            # Try to find existing user by email
            user = User.objects.get(email=email)
            self.stdout.write(f'✅ Found existing user: {user.username} ({user.email})')
        except User.DoesNotExist:
            # Create new admin user
            username = 'melaku_admin'
            # Ensure username is unique
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f'melaku_admin_{counter}'
                counter += 1
            
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name='Melaku',
                last_name='Garsamo',
            )
            self.stdout.write(f'✅ Created new user: {user.username} ({user.email})')
        
        # Ensure user is admin
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        
        # Create or update UserProfile
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'email_verified': True,
                'phone_verified': False,
                'is_agent': True,
                'company_name': 'Ereft Realty',
            }
        )
        
        if not created:
            profile.email_verified = True
            profile.is_agent = True
            profile.company_name = 'Ereft Realty'
            profile.save()
        
        self.stdout.write(self.style.SUCCESS(
            f'✅ Admin user configured: {user.username} ({user.email})\n'
            f'   - is_staff: {user.is_staff}\n'
            f'   - is_superuser: {user.is_superuser}\n'
            f'   - is_active: {user.is_active}'
        ))
        
        self.stdout.write(
            f'\n🔐 Admin credentials:\n'
            f'   Username: {user.username}\n'
            f'   Email: {user.email}\n'
            f'   Password: (set via Django admin or password reset)'
        )

