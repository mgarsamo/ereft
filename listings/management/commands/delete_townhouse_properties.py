from django.core.management.base import BaseCommand
from listings.models import Property, PropertyImage, Favorite
from django.core.cache import cache
from django.db import transaction

class Command(BaseCommand):
    help = 'Permanently delete all townhouse properties from the system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion (required for actual deletion)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        confirm = options['confirm']
        
        # Find all townhouse properties
        townhouse_properties = Property.objects.filter(property_type='townhouse')
        count = townhouse_properties.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('✓ No townhouse properties found. Nothing to delete.')
            )
            return
        
        self.stdout.write(
            self.style.WARNING(f'Found {count} townhouse propert{"y" if count == 1 else "ies"} to delete.')
        )
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n=== DRY RUN MODE ==='))
            self.stdout.write('Properties that would be deleted:')
            for prop in townhouse_properties:
                self.stdout.write(f'  - {prop.id}: {prop.title} ({prop.city}, {prop.sub_city or "N/A"})')
            self.stdout.write(f'\nTotal: {count} properties would be deleted.')
            self.stdout.write('\nTo actually delete, run: python manage.py delete_townhouse_properties --confirm')
            return
        
        if not confirm:
            self.stdout.write(
                self.style.ERROR(
                    '\n⚠️  DELETION NOT CONFIRMED!\n'
                    'This will permanently delete all townhouse properties.\n'
                    'To confirm deletion, run: python manage.py delete_townhouse_properties --confirm'
                )
            )
            return
        
        # Proceed with deletion
        self.stdout.write(self.style.WARNING('\n⚠️  Starting deletion of townhouse properties...'))
        
        deleted_count = 0
        deleted_ids = []
        
        try:
            with transaction.atomic():
                for prop in townhouse_properties:
                    prop_id = prop.id
                    prop_title = prop.title
                    
                    # Delete related PropertyImage objects
                    PropertyImage.objects.filter(property=prop).delete()
                    
                    # Delete related Favorite objects
                    Favorite.objects.filter(property=prop).delete()
                    
                    # Delete the property itself
                    prop.delete()
                    
                    deleted_count += 1
                    deleted_ids.append(str(prop_id))
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✓ Deleted: {prop_title} ({prop_id})')
                    )
                
                # Clear cache to ensure deleted properties don't appear
                cache.clear()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n✅ Successfully deleted {deleted_count} townhouse propert{"y" if deleted_count == 1 else "ies"}.'
                    )
                )
                self.stdout.write(f'Deleted property IDs: {", ".join(deleted_ids[:10])}' + 
                                (f' ... and {len(deleted_ids) - 10} more' if len(deleted_ids) > 10 else ''))
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\n❌ Error during deletion: {str(e)}')
            )
            raise
