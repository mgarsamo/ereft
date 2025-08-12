from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from listings.models import Property, PropertyImage, Neighborhood
from decimal import Decimal
import uuid

class Command(BaseCommand):
    help = 'Populate database with sample property data for testing'

    def handle(self, *args, **options):
        self.stdout.write('🏠 Starting to populate sample property data...')
        
        # Create a test user if it doesn't exist
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
            self.stdout.write('✅ Created test user: test_user')
        else:
            self.stdout.write('✅ Test user already exists')
        
        # Sample properties data
        sample_properties = [
            {
                'title': 'Beautiful House in Bole',
                'description': 'Spacious 4-bedroom house with modern amenities in prime Bole location. Features include garden, garage, and stunning city views.',
                'property_type': 'house',
                'listing_type': 'sale',
                'price': Decimal('2500000'),
                'address': 'Bole District, Addis Ababa',
                'city': 'Addis Ababa',
                'sub_city': 'Bole',
                'kebele': '03',
                'street_name': 'Bole Road',
                'house_number': '123',
                'country': 'Ethiopia',
                'latitude': Decimal('9.0192'),
                'longitude': Decimal('38.7525'),
                'bedrooms': 4,
                'bathrooms': Decimal('3.0'),
                'area_sqm': 250,
                'lot_size_sqm': 300,
                'year_built': 2020,
                'has_garage': True,
                'has_pool': False,
                'has_garden': True,
                'has_balcony': True,
                'is_furnished': False,
                'has_air_conditioning': True,
                'has_heating': False,
                'is_featured': True,
                'status': 'active',
                'is_published': True,
                'is_active': True,
                'views_count': 45
            },
            {
                'title': 'Modern Apartment in Kazanchis',
                'description': 'Contemporary 3-bedroom apartment with city skyline views. Fully furnished with modern appliances and security system.',
                'property_type': 'apartment',
                'listing_type': 'rent',
                'price': Decimal('15000'),
                'address': 'Kazanchis District, Addis Ababa',
                'city': 'Addis Ababa',
                'sub_city': 'Arada',
                'kebele': '07',
                'street_name': 'Kazanchis Street',
                'house_number': '456',
                'country': 'Ethiopia',
                'latitude': Decimal('9.0300'),
                'longitude': Decimal('38.7400'),
                'bedrooms': 3,
                'bathrooms': Decimal('2.0'),
                'area_sqm': 180,
                'lot_size_sqm': 200,
                'year_built': 2022,
                'has_garage': False,
                'has_pool': False,
                'has_garden': False,
                'has_balcony': True,
                'is_furnished': True,
                'has_air_conditioning': True,
                'has_heating': False,
                'is_featured': True,
                'status': 'active',
                'is_published': True,
                'is_active': True,
                'views_count': 32
            },
            {
                'title': 'Commercial Space in Merkato',
                'description': 'Prime commercial space in busy Merkato area. High foot traffic, perfect for retail or office use.',
                'property_type': 'commercial',
                'listing_type': 'rent',
                'price': Decimal('25000'),
                'address': 'Merkato District, Addis Ababa',
                'city': 'Addis Ababa',
                'sub_city': 'Addis Ketema',
                'kebele': '02',
                'street_name': 'Merkato Main Street',
                'house_number': '789',
                'country': 'Ethiopia',
                'latitude': Decimal('9.0100'),
                'longitude': Decimal('38.7200'),
                'bedrooms': 0,
                'bathrooms': Decimal('2.0'),
                'area_sqm': 300,
                'lot_size_sqm': 350,
                'year_built': 2018,
                'has_garage': True,
                'has_pool': False,
                'has_garden': False,
                'has_balcony': False,
                'is_furnished': False,
                'has_air_conditioning': True,
                'has_heating': False,
                'is_featured': False,
                'status': 'active',
                'is_published': True,
                'is_active': True,
                'views_count': 28
            },
            {
                'title': 'Luxury Villa in CMC',
                'description': 'Exclusive 5-bedroom luxury villa with private pool, garden, and panoramic city views. Premium finishes throughout.',
                'property_type': 'house',
                'listing_type': 'sale',
                'price': Decimal('5500000'),
                'address': 'CMC Area, Addis Ababa',
                'city': 'Addis Ababa',
                'sub_city': 'Bole',
                'kebele': '05',
                'street_name': 'CMC Road',
                'house_number': '101',
                'country': 'Ethiopia',
                'latitude': Decimal('9.0180'),
                'longitude': Decimal('38.7580'),
                'bedrooms': 5,
                'bathrooms': Decimal('4.0'),
                'area_sqm': 400,
                'lot_size_sqm': 500,
                'year_built': 2023,
                'has_garage': True,
                'has_pool': True,
                'has_garden': True,
                'has_balcony': True,
                'is_furnished': True,
                'has_air_conditioning': True,
                'has_heating': True,
                'is_featured': True,
                'status': 'active',
                'is_published': True,
                'is_active': True,
                'views_count': 67
            },
            {
                'title': 'Townhouse in Kolfe',
                'description': 'Modern 3-bedroom townhouse with private entrance and small garden. Perfect for families seeking privacy.',
                'property_type': 'townhouse',
                'listing_type': 'sale',
                'price': Decimal('1800000'),
                'address': 'Kolfe District, Addis Ababa',
                'city': 'Addis Ababa',
                'sub_city': 'Kolfe',
                'kebele': '08',
                'street_name': 'Kolfe Street',
                'house_number': '202',
                'country': 'Ethiopia',
                'latitude': Decimal('9.0089'),
                'longitude': Decimal('38.7389'),
                'bedrooms': 3,
                'bathrooms': Decimal('2.5'),
                'area_sqm': 200,
                'lot_size_sqm': 250,
                'year_built': 2021,
                'has_garage': True,
                'has_pool': False,
                'has_garden': True,
                'has_balcony': True,
                'is_furnished': False,
                'has_air_conditioning': True,
                'has_heating': False,
                'is_featured': False,
                'status': 'active',
                'is_published': True,
                'is_active': True,
                'views_count': 23
            }
        ]
        
        properties_created = 0
        
        for prop_data in sample_properties:
            # Check if property already exists
            if not Property.objects.filter(title=prop_data['title']).exists():
                # Create the property
                property_obj = Property.objects.create(
                    owner=test_user,
                    **prop_data
                )
                
                # Create sample images for the property
                sample_images = [
                    {
                        'image': 'https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=800',
                        'caption': 'Front view',
                        'is_primary': True,
                        'order': 0
                    },
                    {
                        'image': 'https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=800',
                        'caption': 'Living room',
                        'is_primary': False,
                        'order': 1
                    },
                    {
                        'image': 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800',
                        'caption': 'Kitchen',
                        'is_primary': False,
                        'order': 2
                    }
                ]
                
                for img_data in sample_images:
                    PropertyImage.objects.create(
                        property=property_obj,
                        **img_data
                    )
                
                properties_created += 1
                self.stdout.write(f'✅ Created property: {prop_data["title"]}')
            else:
                self.stdout.write(f'⏭️ Property already exists: {prop_data["title"]}')
        
        self.stdout.write(f'🎉 Successfully created {properties_created} new properties!')
        self.stdout.write(f'📊 Total properties in database: {Property.objects.count()}')
        self.stdout.write(f'⭐ Featured properties: {Property.objects.filter(is_featured=True).count()}')
        self.stdout.write(f'🏠 Active properties: {Property.objects.filter(is_active=True).count()}')
