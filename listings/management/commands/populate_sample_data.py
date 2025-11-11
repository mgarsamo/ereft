from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from listings.models import Property, PropertyImage, Neighborhood, UserProfile
from decimal import Decimal
from django.core.cache import cache
from django.utils import timezone

class Command(BaseCommand):
    help = 'Populate database with sample property data for testing'

    def handle(self, *args, **options):
        self.stdout.write('🏠 Starting to populate sample property data...')
        
        # Create or update the production listing agent profile
        agent_user, created = User.objects.get_or_create(
            username='melaku_agent',
            defaults={
                'email': 'melaku.garsamo@gmail.com',
                'first_name': 'Melaku',
                'last_name': 'Garsamo',
                'is_active': True,
            },
        )

        if created:
            agent_user.set_password('ereftstrongpassword')

        # Ensure agent details stay up to date
        agent_user.email = 'melaku.garsamo@gmail.com'
        agent_user.first_name = 'Melaku'
        agent_user.last_name = 'Garsamo'
        agent_user.save()

        agent_profile, _ = UserProfile.objects.get_or_create(user=agent_user)
        agent_profile.phone_number = '+251 966 913 617'
        agent_profile.is_agent = True
        agent_profile.company_name = 'Ereft Realty'
        agent_profile.email_verified = True
        agent_profile.phone_verified = True
        agent_profile.save()

        self.stdout.write('✅ Listing agent profile ready: melaku.garsamo@gmail.com / +251 966 913 617')
 
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
                'views_count': 45,
                'listed_date': timezone.now(),
                'images': [
                    {
                        'url': 'https://images.unsplash.com/photo-1600585154340-0ef3c08dc63f?w=1200&q=80',
                        'caption': 'Front elevation with landscaped garden',
                    },
                    {
                        'url': 'https://images.unsplash.com/photo-1502672023488-70e25813eb80?w=1200&q=80',
                        'caption': 'Sunlit living room with hardwood floors',
                    },
                    {
                        'url': 'https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=1200&q=80',
                        'caption': 'Modern kitchen with breakfast nook',
                    },
                ],
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
                'views_count': 32,
                'listed_date': timezone.now(),
                'images': [
                    {
                        'url': 'https://images.unsplash.com/photo-1505693314120-0d443867891c?w=1200&q=80',
                        'caption': 'Open-concept apartment living area',
                    },
                    {
                        'url': 'https://images.unsplash.com/photo-1484154218962-a197022b5858?w=1200&q=80',
                        'caption': 'City skyline view from balcony',
                    },
                    {
                        'url': 'https://images.unsplash.com/photo-1519710164239-da123dc03ef4?w=1200&q=80',
                        'caption': 'Primary bedroom with ensuite',
                    },
                ],
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
                'views_count': 28,
                'listed_date': timezone.now(),
                'images': [
                    {
                        'url': 'https://images.unsplash.com/photo-1505691938895-1758d7feb511?w=1200&q=80',
                        'caption': 'Storefront facing high-traffic street',
                    },
                    {
                        'url': 'https://images.unsplash.com/photo-1531973576160-7125cd663d86?w=1200&q=80',
                        'caption': 'Spacious commercial interior',
                    },
                    {
                        'url': 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=1200&q=80',
                        'caption': 'Rear access and loading area',
                    },
                ],
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
                'views_count': 67,
                'listed_date': timezone.now(),
                'images': [
                    {
                        'url': 'https://images.unsplash.com/photo-1616594039964-5e2b46b9aae1?w=1200&q=80',
                        'caption': 'Villa exterior with infinity pool',
                    },
                    {
                        'url': 'https://images.unsplash.com/photo-1600210491370-9bb39d1dc651?w=1200&q=80',
                        'caption': 'Grand foyer with double staircase',
                    },
                    {
                        'url': 'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=1200&q=80',
                        'caption': 'Gourmet kitchen and dining area',
                    },
                ],
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
                'views_count': 23,
                'listed_date': timezone.now(),
                'images': [
                    {
                        'url': 'https://images.unsplash.com/photo-1489515217757-5fd1be406fef?w=1200&q=80',
                        'caption': 'Townhouse front elevation',
                    },
                    {
                        'url': 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=1200&q=80',
                        'caption': 'Family-friendly living space',
                    },
                    {
                        'url': 'https://images.unsplash.com/photo-1560184897-ae75f418493e?w=1200&q=80',
                        'caption': 'Spacious backyard patio',
                    },
                ],
            }
        ]
 
        properties_created = 0
 
        for prop_data in sample_properties:
            prop_payload = prop_data.copy()
            images_payload = prop_payload.pop('images', [])

            area = prop_payload.get('area_sqm') or 0
            if area:
                prop_payload['price_per_sqm'] = (prop_payload['price'] / Decimal(area)).quantize(Decimal('0.01'))

            property_obj, created = Property.objects.get_or_create(
                title=prop_payload['title'],
                defaults={**prop_payload, 'owner': agent_user},
            )

            if created:
                self.stdout.write(f'✅ Created property: {prop_payload["title"]}')
            else:
                for field, value in prop_payload.items():
                    setattr(property_obj, field, value)
                property_obj.owner = agent_user
                property_obj.save()
                self.stdout.write(f'🔄 Updated property: {prop_payload["title"]}')

            # Refresh property images with curated gallery
            PropertyImage.objects.filter(property=property_obj).delete()

            for order, image_entry in enumerate(images_payload):
                PropertyImage.objects.create(
                    property=property_obj,
                    image=image_entry['url'],
                    caption=image_entry.get('caption'),
                    is_primary=(order == 0),
                    order=order,
                )

            properties_created += 1 if created else 0
 
        cache.clear()
        self.stdout.write('🧹 Cache cleared to reflect latest property data')
        self.stdout.write(f'🎉 Successfully created {properties_created} new properties!')
        self.stdout.write(f'📊 Total properties in database: {Property.objects.count()}')
        self.stdout.write(f'⭐ Featured properties: {Property.objects.filter(is_featured=True).count()}')
        self.stdout.write(f'🏠 Active properties: {Property.objects.filter(is_active=True).count()}')
