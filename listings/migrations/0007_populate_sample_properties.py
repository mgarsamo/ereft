from decimal import Decimal

from django.contrib.auth.hashers import make_password
from django.db import migrations


def create_sample_properties(apps, schema_editor):
    Property = apps.get_model('listings', 'Property')
    PropertyImage = apps.get_model('listings', 'PropertyImage')
    User = apps.get_model('auth', 'User')
    UserProfile = apps.get_model('listings', 'UserProfile')

    sample_owner, created = User.objects.get_or_create(
        username='sample_agent',
        defaults={
            'email': 'agent@ereft.com',
            'first_name': 'Sample',
            'last_name': 'Agent',
            'is_active': True,
        },
    )
    if created:
        sample_owner.password = make_password('SampleAgent123!')
        sample_owner.save()

    UserProfile.objects.get_or_create(
        user=sample_owner,
        defaults={
            'phone_number': '+251911123456',
            'email_verified': True,
            'is_agent': True,
        },
    )

    sample_properties = [
        {
            'title': 'Luxury Villa in Bole',
            'description': (
                'Five-bedroom luxury villa with private pool, landscaped garden, '
                'and panoramic city views. Premium finishes and smart home features throughout.'
            ),
            'property_type': 'house',
            'listing_type': 'sale',
            'price': Decimal('5500000'),
            'address': 'Bole CMC Road',
            'city': 'Addis Ababa',
            'sub_city': 'Bole',
            'kebele': '05',
            'street_name': 'CMC Road',
            'house_number': '101',
            'country': 'Ethiopia',
            'latitude': Decimal('9.018000'),
            'longitude': Decimal('38.758000'),
            'bedrooms': 5,
            'bathrooms': Decimal('4.0'),
            'area_sqm': 420,
            'lot_size_sqm': 520,
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
            'views_count': 64,
            'images': [
                'https://images.unsplash.com/photo-1613977256644-1ecc70409f93?w=1600',
                'https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=1600',
                'https://images.unsplash.com/photo-1505691938895-1758d7feb511?w=1600',
            ],
        },
        {
            'title': 'Modern Apartment in Kazanchis',
            'description': (
                'Contemporary three-bedroom apartment with skyline views. '
                'Fully furnished, secure building with underground parking.'
            ),
            'property_type': 'apartment',
            'listing_type': 'rent',
            'price': Decimal('18000'),
            'address': 'Kazanchis',
            'city': 'Addis Ababa',
            'sub_city': 'Arada',
            'kebele': '07',
            'street_name': 'Kazanchis Street',
            'house_number': '8A',
            'country': 'Ethiopia',
            'latitude': Decimal('9.030000'),
            'longitude': Decimal('38.740000'),
            'bedrooms': 3,
            'bathrooms': Decimal('2.0'),
            'area_sqm': 185,
            'lot_size_sqm': 0,
            'year_built': 2022,
            'has_garage': True,
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
            'views_count': 37,
            'images': [
                'https://images.unsplash.com/photo-1505691938895-1758d7feb511?w=1600',
                'https://images.unsplash.com/photo-1449844908441-8829872d2607?w=1600',
                'https://images.unsplash.com/photo-1505691723518-36a5ac3be353?w=1600',
            ],
        },
        {
            'title': 'Commercial Space in Merkato',
            'description': (
                'Prime ground-floor commercial unit with heavy foot traffic. '
                'Perfect for retail, bank branch or flagship showroom.'
            ),
            'property_type': 'commercial',
            'listing_type': 'rent',
            'price': Decimal('26000'),
            'address': 'Merkato Main Street',
            'city': 'Addis Ababa',
            'sub_city': 'Addis Ketema',
            'kebele': '02',
            'street_name': 'Merkato Main Street',
            'house_number': '12',
            'country': 'Ethiopia',
            'latitude': Decimal('9.010000'),
            'longitude': Decimal('38.720000'),
            'bedrooms': 0,
            'bathrooms': Decimal('2.0'),
            'area_sqm': 320,
            'lot_size_sqm': 0,
            'year_built': 2019,
            'has_garage': False,
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
            'views_count': 22,
            'images': [
                'https://images.unsplash.com/photo-1505691938895-1758d7feb511?w=1600',
                'https://images.unsplash.com/photo-1529429617124-aee07fc08957?w=1600',
            ],
        },
    ]

    for property_data in sample_properties:
        images = property_data.pop('images', [])

        property_obj, created = Property.objects.get_or_create(
            title=property_data['title'],
            defaults={**property_data, 'owner': sample_owner},
        )

        if created:
            for order, image_url in enumerate(images):
                PropertyImage.objects.create(
                    property=property_obj,
                    image=image_url,
                    is_primary=(order == 0),
                    order=order,
                )
        elif not property_obj.images.exists():
            for order, image_url in enumerate(images):
                PropertyImage.objects.get_or_create(
                    property=property_obj,
                    image=image_url,
                    defaults={
                        'is_primary': order == 0,
                        'order': order,
                    },
                )


def remove_sample_properties(apps, schema_editor):
    Property = apps.get_model('listings', 'Property')
    User = apps.get_model('auth', 'User')

    Property.objects.filter(owner__username='sample_agent').delete()
    User.objects.filter(username='sample_agent').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0006_make_bedrooms_bathrooms_optional'),
    ]

    operations = [
        migrations.RunPython(create_sample_properties, remove_sample_properties),
    ]

