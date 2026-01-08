"""
Django management command to update all properties to 'active' status
"""
from django.core.management.base import BaseCommand
from listings.models import Property


class Command(BaseCommand):
    help = 'Update all properties to have status="active"'

    def handle(self, *args, **options):
        # Update all properties without status or with null status to 'active'
        properties_updated = Property.objects.filter(
            status__in=['', None]
        ).update(status='active')
        
        # Also update any properties that might have invalid status
        all_properties = Property.objects.all()
        total_updated = 0
        
        for prop in all_properties:
            if not prop.status or prop.status not in ['active', 'pending', 'inactive', 'sold', 'rented']:
                prop.status = 'active'
                prop.save()
                total_updated += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated {properties_updated + total_updated} properties to status="active"'
            )
        )
