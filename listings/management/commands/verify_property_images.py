# FILE: ereft_api/listings/management/commands/verify_property_images.py

from django.core.management.base import BaseCommand
from listings.models import Property, PropertyImage


class Command(BaseCommand):
    help = 'Verify PropertyImage objects exist for all properties and display their URLs'

    def handle(self, *args, **options):
        self.stdout.write("🔍 Verifying PropertyImage objects...")
        
        properties = Property.objects.all()
        total_properties = properties.count()
        
        self.stdout.write(f"\n📊 Total properties: {total_properties}")
        
        properties_with_images = 0
        properties_without_images = 0
        total_images = 0
        
        for property_obj in properties:
            images = PropertyImage.objects.filter(property=property_obj)
            image_count = images.count()
            
            if image_count > 0:
                properties_with_images += 1
                total_images += image_count
                
                self.stdout.write(f"\n✅ Property: {property_obj.title[:50]}...")
                self.stdout.write(f"   ID: {property_obj.id}")
                self.stdout.write(f"   Images: {image_count}")
                
                for idx, img in enumerate(images.order_by('order', 'created_at'), 1):
                    url = img.image or 'NO URL'
                    self.stdout.write(f"   Image {idx}: {url[:80]}...")
                    self.stdout.write(f"      - ID: {img.id}, Primary: {img.is_primary}, Order: {img.order}")
            else:
                properties_without_images += 1
                self.stdout.write(f"\n⚠️ Property: {property_obj.title[:50]}...")
                self.stdout.write(f"   ID: {property_obj.id}")
                self.stdout.write(f"   ❌ NO IMAGES")
        
        self.stdout.write(f"\n📈 Summary:")
        self.stdout.write(f"   Properties with images: {properties_with_images}")
        self.stdout.write(f"   Properties without images: {properties_without_images}")
        self.stdout.write(f"   Total images: {total_images}")
        
        if properties_without_images > 0:
            self.stdout.write(self.style.WARNING(
                f"\n⚠️ {properties_without_images} properties are missing images!"
            ))
