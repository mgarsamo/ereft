"""
Management command to ensure all admin emails have admin privileges
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Ensure all admin emails have admin privileges (is_staff and is_superuser)'

    def handle(self, *args, **options):
        admin_emails = [
            'admin@ereft.com',
            'melaku.garsamo@gmail.com',
            'cb.garsamo@gmail.com',
            'lydiageleta45@gmail.com'
        ]
        
        updated_count = 0
        created_count = 0
        
        for email in admin_emails:
            try:
                # Find user by email (handle duplicates)
                users = User.objects.filter(email=email)
                
                if users.exists():
                    for user in users:
                        if not user.is_staff or not user.is_superuser:
                            user.is_staff = True
                            user.is_superuser = True
                            user.is_active = True
                            user.save()
                            updated_count += 1
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'✅ Updated admin privileges for: {email} (ID: {user.id}, Username: {user.username})'
                                )
                            )
                        else:
                            self.stdout.write(
                                f'ℹ️  User {email} (ID: {user.id}) already has admin privileges'
                            )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠️  User with email {email} not found. They will get admin privileges on next login.'
                        )
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ Error processing {email}: {str(e)}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Admin privilege check complete. Updated: {updated_count} user(s).'
            )
        )
