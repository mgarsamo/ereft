from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from listings.models import Property, PropertyImage, Neighborhood, UserProfile
from decimal import Decimal
from django.core.cache import cache
from django.utils import timezone

class Command(BaseCommand):
    help = 'Populate database with comprehensive sample property data'

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
        
        # Comprehensive sample properties data - 25+ properties across all types
        sample_properties = [
            # HOUSES FOR SALE
            {
                'title': 'Luxury Villa in Bole with Pool',
                'description': 'Stunning 5-bedroom villa with private pool, landscaped garden, and panoramic city views. Premium finishes, smart home system, and 24/7 security.',
                'property_type': 'house',
                'listing_type': 'sale',
                'price': Decimal('8500000'),
                'address': 'Bole Atlas, Addis Ababa',
                'city': 'Addis Ababa',
                'sub_city': 'Bole',
                'kebele': '03',
                'country': 'Ethiopia',
                'latitude': Decimal('9.0192'),
                'longitude': Decimal('38.7525'),
                'bedrooms': 5,
                'bathrooms': Decimal('4.5'),
                'area_sqm': 450,
                'year_built': 2023,
                'has_garage': True,
                'has_pool': True,
                'has_garden': True,
                'has_balcony': True,
                'is_furnished': True,
                'has_air_conditioning': True,
                'is_featured': True,
                'status': 'active',
                'images': [
                    {'url': 'https://images.pexels.com/photos/1396122/pexels-photo-1396122.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Luxury villa exterior with pool'},
                    {'url': 'https://images.pexels.com/photos/2635038/pexels-photo-2635038.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Infinity pool and garden'},
                    {'url': 'https://images.pexels.com/photos/1571460/pexels-photo-1571460.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Spacious living room'},
                    {'url': 'https://images.pexels.com/photos/1643383/pexels-photo-1643383.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Modern kitchen'},
                ],
            },
            {
                'title': 'Modern Family Home in CMC',
                'description': 'Beautiful 4-bedroom family home with large backyard, perfect for children. Close to international schools and shopping centers.',
                'property_type': 'house',
                'listing_type': 'sale',
                'price': Decimal('4200000'),
                'address': 'CMC Area, Addis Ababa',
                'city': 'Addis Ababa',
                'sub_city': 'Bole',
                'kebele': '05',
                'country': 'Ethiopia',
                'latitude': Decimal('9.0180'),
                'longitude': Decimal('38.7580'),
                'bedrooms': 4,
                'bathrooms': Decimal('3.0'),
                'area_sqm': 320,
                'year_built': 2021,
                'has_garage': True,
                'has_garden': True,
                'has_balcony': True,
                'is_featured': True,
                'status': 'active',
                'images': [
                    {'url': 'https://images.pexels.com/photos/186077/pexels-photo-186077.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Modern family home'},
                    {'url': 'https://images.pexels.com/photos/1571471/pexels-photo-1571471.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Bright living area'},
                    {'url': 'https://images.pexels.com/photos/1457842/pexels-photo-1457842.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Family kitchen'},
                ],
            },
            {
                'title': 'Charming House in Old Airport',
                'description': 'Classic 3-bedroom house with character and charm. Recently renovated with modern amenities while maintaining original features.',
                'property_type': 'house',
                'listing_type': 'sale',
                'price': Decimal('3200000'),
                'address': 'Old Airport Area, Addis Ababa',
                'city': 'Addis Ababa',
                'sub_city': 'Bole',
                'kebele': '12',
                'country': 'Ethiopia',
                'latitude': Decimal('9.0050'),
                'longitude': Decimal('38.7620'),
                'bedrooms': 3,
                'bathrooms': Decimal('2.0'),
                'area_sqm': 220,
                'year_built': 2018,
                'has_garage': True,
                'has_garden': True,
                'status': 'active',
                'images': [
                    {'url': 'https://images.pexels.com/photos/280229/pexels-photo-280229.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Charming house exterior'},
                    {'url': 'https://images.pexels.com/photos/1648776/pexels-photo-1648776.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Cozy living room'},
                ],
            },
            
            # APARTMENTS FOR RENT
            {
                'title': 'Penthouse Apartment in Kazanchis',
                'description': 'Luxurious penthouse with 360-degree city views. 3 bedrooms, fully furnished with designer furniture, gym access, and concierge service.',
                'property_type': 'apartment',
                'listing_type': 'rent',
                'price': Decimal('35000'),
                'address': 'Kazanchis, Addis Ababa',
                'city': 'Addis Ababa',
                'sub_city': 'Arada',
                'kebele': '07',
                'country': 'Ethiopia',
                'latitude': Decimal('9.0300'),
                'longitude': Decimal('38.7400'),
                'bedrooms': 3,
                'bathrooms': Decimal('2.5'),
                'area_sqm': 200,
                'year_built': 2023,
                'is_furnished': True,
                'has_air_conditioning': True,
                'has_balcony': True,
                'is_featured': True,
                'status': 'active',
                'images': [
                    {'url': 'https://images.pexels.com/photos/1457842/pexels-photo-1457842.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Penthouse living area'},
                    {'url': 'https://images.pexels.com/photos/271624/pexels-photo-271624.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Panoramic city views'},
                    {'url': 'https://images.pexels.com/photos/1918291/pexels-photo-1918291.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Modern bedroom'},
                ],
            },
            {
                'title': 'Cozy 2BR Apartment in Piassa',
                'description': 'Affordable 2-bedroom apartment in historic Piassa area. Walking distance to restaurants, cafes, and public transport.',
                'property_type': 'apartment',
                'listing_type': 'rent',
                'price': Decimal('12000'),
                'address': 'Piassa, Addis Ababa',
                'city': 'Addis Ababa',
                'sub_city': 'Arada',
                'kebele': '15',
                'country': 'Ethiopia',
                'latitude': Decimal('9.0320'),
                'longitude': Decimal('38.7450'),
                'bedrooms': 2,
                'bathrooms': Decimal('1.0'),
                'area_sqm': 85,
                'year_built': 2019,
                'is_furnished': False,
                'status': 'active',
                'images': [
                    {'url': 'https://images.pexels.com/photos/439227/pexels-photo-439227.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Cozy apartment interior'},
                    {'url': 'https://images.pexels.com/photos/271795/pexels-photo-271795.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Comfortable living space'},
                ],
            },
            {
                'title': 'Studio Apartment in Megenagna',
                'description': 'Modern studio apartment perfect for young professionals. Fully furnished with high-speed internet and utilities included.',
                'property_type': 'apartment',
                'listing_type': 'rent',
                'price': Decimal('8000'),
                'address': 'Megenagna, Addis Ababa',
                'city': 'Addis Ababa',
                'sub_city': 'Bole',
                'kebele': '18',
                'country': 'Ethiopia',
                'latitude': Decimal('9.0150'),
                'longitude': Decimal('38.7700'),
                'bedrooms': 1,
                'bathrooms': Decimal('1.0'),
                'area_sqm': 45,
                'year_built': 2022,
                'is_furnished': True,
                'has_air_conditioning': True,
                'status': 'active',
                'images': [
                    {'url': 'https://images.pexels.com/photos/1457847/pexels-photo-1457847.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Modern studio layout'},
                    {'url': 'https://images.pexels.com/photos/1329711/pexels-photo-1329711.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Efficient living space'},
                ],
            },
            
            # CONDOS FOR SALE
            {
                'title': 'Luxury Condo in Sarbet',
                'description': 'Brand new 3-bedroom condo with premium finishes. Building features include gym, swimming pool, and rooftop terrace.',
                'property_type': 'condo',
                'listing_type': 'sale',
                'price': Decimal('5200000'),
                'address': 'Sarbet, Addis Ababa',
                'city': 'Addis Ababa',
                'sub_city': 'Kirkos',
                'kebele': '09',
                'country': 'Ethiopia',
                'latitude': Decimal('9.0100'),
                'longitude': Decimal('38.7550'),
                'bedrooms': 3,
                'bathrooms': Decimal('2.5'),
                'area_sqm': 165,
                'year_built': 2024,
                'has_pool': True,
                'has_air_conditioning': True,
                'has_balcony': True,
                'is_featured': True,
                'status': 'active',
                'images': [
                    {'url': 'https://images.pexels.com/photos/1643383/pexels-photo-1643383.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Luxury condo interior'},
                    {'url': 'https://images.pexels.com/photos/1571463/pexels-photo-1571463.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Modern finishes'},
                    {'url': 'https://images.pexels.com/photos/1350789/pexels-photo-1350789.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Building amenities'},
                ],
            },
            {
                'title': 'Affordable Condo in 22 Mazoria',
                'description': '2-bedroom condo in growing neighborhood. Great investment opportunity with high rental demand.',
                'property_type': 'condo',
                'listing_type': 'sale',
                'price': Decimal('2800000'),
                'address': '22 Mazoria, Addis Ababa',
                'city': 'Addis Ababa',
                'sub_city': 'Yeka',
                'kebele': '11',
                'country': 'Ethiopia',
                'latitude': Decimal('9.0250'),
                'longitude': Decimal('38.7850'),
                'bedrooms': 2,
                'bathrooms': Decimal('1.5'),
                'area_sqm': 95,
                'year_built': 2020,
                'has_balcony': True,
                'status': 'active',
                'images': [
                    {'url': 'https://images.pexels.com/photos/259962/pexels-photo-259962.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Affordable condo'},
                    {'url': 'https://images.pexels.com/photos/271643/pexels-photo-271643.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Well-maintained interior'},
                ],
            },
            
            # TOWNHOUSES FOR SALE
            {
                'title': 'Modern Townhouse in Kolfe',
                'description': 'Contemporary 3-bedroom townhouse with private entrance and garden. Perfect for families seeking privacy and community.',
                'property_type': 'townhouse',
                'listing_type': 'sale',
                'price': Decimal('3600000'),
                'address': 'Kolfe, Addis Ababa',
                'city': 'Addis Ababa',
                'sub_city': 'Kolfe',
                'kebele': '08',
                'country': 'Ethiopia',
                'latitude': Decimal('9.0089'),
                'longitude': Decimal('38.7389'),
                'bedrooms': 3,
                'bathrooms': Decimal('2.5'),
                'area_sqm': 180,
                'year_built': 2021,
                'has_garage': True,
                'has_garden': True,
                'is_featured': False,
                'status': 'active',
                'images': [
                    {'url': 'https://images.pexels.com/photos/259588/pexels-photo-259588.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Modern townhouse'},
                    {'url': 'https://images.pexels.com/photos/1396132/pexels-photo-1396132.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Private garden'},
                ],
            },
            {
                'title': 'Spacious Townhouse in Gerji',
                'description': '4-bedroom townhouse with finished basement. Great for growing families with plenty of storage space.',
                'property_type': 'townhouse',
                'listing_type': 'sale',
                'price': Decimal('4100000'),
                'address': 'Gerji, Addis Ababa',
                'city': 'Addis Ababa',
                'sub_city': 'Bole',
                'kebele': '14',
                'country': 'Ethiopia',
                'latitude': Decimal('9.0280'),
                'longitude': Decimal('38.7920'),
                'bedrooms': 4,
                'bathrooms': Decimal('3.0'),
                'area_sqm': 240,
                'year_built': 2020,
                'has_garage': True,
                'has_garden': True,
                'status': 'active',
                'images': [
                    {'url': 'https://images.pexels.com/photos/1438832/pexels-photo-1438832.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Spacious townhouse'},
                    {'url': 'https://images.pexels.com/photos/1571468/pexels-photo-1571468.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Family-friendly layout'},
                ],
            },
            
            # LAND FOR SALE
            {
                'title': 'Prime Land in Lebu',
                'description': 'Excellent 500sqm plot in rapidly developing Lebu area. Perfect for building your dream home or investment property.',
                'property_type': 'land',
                'listing_type': 'sale',
                'price': Decimal('2500000'),
                'address': 'Lebu, Addis Ababa',
                'city': 'Addis Ababa',
                'sub_city': 'Gulele',
                'kebele': '06',
                'country': 'Ethiopia',
                'latitude': Decimal('9.0450'),
                'longitude': Decimal('38.7200'),
                'bedrooms': 0,
                'bathrooms': Decimal('0'),
                'area_sqm': 500,
                'lot_size_sqm': 500,
                'status': 'active',
                'images': [
                    {'url': 'https://images.pexels.com/photos/1105766/pexels-photo-1105766.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Prime land plot'},
                    {'url': 'https://images.pexels.com/photos/1268871/pexels-photo-1268871.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Development area'},
                ],
            },
            {
                'title': 'Large Plot in Saris',
                'description': '1000sqm land with road access and utilities available. Ideal for residential or commercial development.',
                'property_type': 'land',
                'listing_type': 'sale',
                'price': Decimal('4500000'),
                'address': 'Saris, Addis Ababa',
                'city': 'Addis Ababa',
                'sub_city': 'Akaki Kality',
                'kebele': '04',
                'country': 'Ethiopia',
                'latitude': Decimal('8.9800'),
                'longitude': Decimal('38.7500'),
                'bedrooms': 0,
                'bathrooms': Decimal('0'),
                'area_sqm': 1000,
                'lot_size_sqm': 1000,
                'is_featured': False,
                'status': 'active',
                'images': [
                    {'url': 'https://images.pexels.com/photos/1179229/pexels-photo-1179229.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Large land plot'},
                    {'url': 'https://images.pexels.com/photos/1105766/pexels-photo-1105766.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Ready for development'},
                ],
            },
            
            # COMMERCIAL PROPERTIES FOR RENT
            {
                'title': 'Prime Office Space in Bole',
                'description': 'Modern 200sqm office space in prestigious Bole location. High-speed internet, parking, and 24/7 security.',
                'property_type': 'commercial',
                'listing_type': 'rent',
                'price': Decimal('45000'),
                'address': 'Bole Road, Addis Ababa',
                'city': 'Addis Ababa',
                'sub_city': 'Bole',
                'kebele': '02',
                'country': 'Ethiopia',
                'latitude': Decimal('9.0150'),
                'longitude': Decimal('38.7600'),
                'bedrooms': 0,
                'bathrooms': Decimal('2.0'),
                'area_sqm': 200,
                'year_built': 2022,
                'has_air_conditioning': True,
                'is_featured': True,
                'status': 'active',
                'images': [
                    {'url': 'https://images.pexels.com/photos/380768/pexels-photo-380768.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Modern office space'},
                    {'url': 'https://images.pexels.com/photos/1181406/pexels-photo-1181406.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Professional workspace'},
                ],
            },
            {
                'title': 'Retail Space in Merkato',
                'description': 'High-traffic retail location in busy Merkato market. Perfect for shop, restaurant, or service business.',
                'property_type': 'commercial',
                'listing_type': 'rent',
                'price': Decimal('28000'),
                'address': 'Merkato, Addis Ababa',
                'city': 'Addis Ababa',
                'sub_city': 'Addis Ketema',
                'kebele': '01',
                'country': 'Ethiopia',
                'latitude': Decimal('9.0100'),
                'longitude': Decimal('38.7200'),
                'bedrooms': 0,
                'bathrooms': Decimal('1.0'),
                'area_sqm': 150,
                'year_built': 2018,
                'status': 'active',
                'images': [
                    {'url': 'https://images.pexels.com/photos/1643389/pexels-photo-1643389.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Retail storefront'},
                    {'url': 'https://images.pexels.com/photos/3184299/pexels-photo-3184299.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Commercial interior'},
                ],
            },
            {
                'title': 'Warehouse in Kaliti',
                'description': 'Large 500sqm warehouse with loading dock and ample parking. Ideal for distribution or manufacturing.',
                'property_type': 'commercial',
                'listing_type': 'rent',
                'price': Decimal('35000'),
                'address': 'Kaliti, Addis Ababa',
                'city': 'Addis Ababa',
                'sub_city': 'Akaki Kality',
                'kebele': '10',
                'country': 'Ethiopia',
                'latitude': Decimal('8.9500'),
                'longitude': Decimal('38.7400'),
                'bedrooms': 0,
                'bathrooms': Decimal('2.0'),
                'area_sqm': 500,
                'year_built': 2019,
                'has_garage': True,
                'status': 'active',
                'images': [
                    {'url': 'https://images.pexels.com/photos/1267338/pexels-photo-1267338.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Warehouse exterior'},
                    {'url': 'https://images.pexels.com/photos/1267360/pexels-photo-1267360.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Storage space'},
                ],
            },
            
            # MORE HOUSES FOR RENT
            {
                'title': 'Family House in Ayat',
                'description': 'Comfortable 3-bedroom house with garden. Quiet neighborhood, close to schools and parks.',
                'property_type': 'house',
                'listing_type': 'rent',
                'price': Decimal('22000'),
                'address': 'Ayat, Addis Ababa',
                'city': 'Addis Ababa',
                'sub_city': 'Bole',
                'kebele': '16',
                'country': 'Ethiopia',
                'latitude': Decimal('8.9950'),
                'longitude': Decimal('38.7800'),
                'bedrooms': 3,
                'bathrooms': Decimal('2.0'),
                'area_sqm': 180,
                'year_built': 2019,
                'has_garden': True,
                'status': 'active',
                'images': [
                    {'url': 'https://images.pexels.com/photos/1029599/pexels-photo-1029599.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Family home'},
                    {'url': 'https://images.pexels.com/photos/1643383/pexels-photo-1643383.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Comfortable interior'},
                ],
            },
            {
                'title': 'Furnished House in Summit',
                'description': 'Fully furnished 4-bedroom house in exclusive Summit area. Ready to move in with all amenities.',
                'property_type': 'house',
                'listing_type': 'rent',
                'price': Decimal('55000'),
                'address': 'Summit, Addis Ababa',
                'city': 'Addis Ababa',
                'sub_city': 'Bole',
                'kebele': '13',
                'country': 'Ethiopia',
                'latitude': Decimal('9.0220'),
                'longitude': Decimal('38.7650'),
                'bedrooms': 4,
                'bathrooms': Decimal('3.5'),
                'area_sqm': 350,
                'year_built': 2022,
                'is_furnished': True,
                'has_garage': True,
                'has_pool': True,
                'has_garden': True,
                'has_air_conditioning': True,
                'is_featured': True,
                'status': 'active',
                'images': [
                    {'url': 'https://images.pexels.com/photos/2635038/pexels-photo-2635038.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Luxury furnished home'},
                    {'url': 'https://images.pexels.com/photos/1571460/pexels-photo-1571460.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Premium finishes'},
                    {'url': 'https://images.pexels.com/photos/1648776/pexels-photo-1648776.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Ready to move in'},
                ],
            },
            
            # MORE APARTMENTS FOR SALE
            {
                'title': 'Investment Apartment in Lideta',
                'description': '2-bedroom apartment with high rental yield. Currently rented, perfect for investors.',
                'property_type': 'apartment',
                'listing_type': 'sale',
                'price': Decimal('2200000'),
                'address': 'Lideta, Addis Ababa',
                'city': 'Addis Ababa',
                'sub_city': 'Lideta',
                'kebele': '05',
                'country': 'Ethiopia',
                'latitude': Decimal('9.0280'),
                'longitude': Decimal('38.7380'),
                'bedrooms': 2,
                'bathrooms': Decimal('1.0'),
                'area_sqm': 75,
                'year_built': 2017,
                'status': 'active',
                'images': [
                    {'url': 'https://images.pexels.com/photos/271624/pexels-photo-271624.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Investment apartment'},
                    {'url': 'https://images.pexels.com/photos/271795/pexels-photo-271795.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Well-maintained unit'},
                ],
            },
            {
                'title': 'Luxury Apartment in Lamberet',
                'description': 'High-end 3-bedroom apartment with imported finishes. Building features include gym, sauna, and rooftop lounge.',
                'property_type': 'apartment',
                'listing_type': 'sale',
                'price': Decimal('6800000'),
                'address': 'Lamberet, Addis Ababa',
                'city': 'Addis Ababa',
                'sub_city': 'Kirkos',
                'kebele': '12',
                'country': 'Ethiopia',
                'latitude': Decimal('9.0050'),
                'longitude': Decimal('38.7500'),
                'bedrooms': 3,
                'bathrooms': Decimal('2.5'),
                'area_sqm': 185,
                'year_built': 2023,
                'is_furnished': True,
                'has_air_conditioning': True,
                'has_balcony': True,
                'is_featured': True,
                'status': 'active',
                'images': [
                    {'url': 'https://images.pexels.com/photos/1457842/pexels-photo-1457842.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Luxury apartment'},
                    {'url': 'https://images.pexels.com/photos/1643383/pexels-photo-1643383.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Premium interior'},
                    {'url': 'https://images.pexels.com/photos/1918291/pexels-photo-1918291.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Designer finishes'},
                ],
            },
            
            # ADDITIONAL VARIETY
            {
                'title': 'Starter Home in Mekanisa',
                'description': 'Affordable 2-bedroom house perfect for first-time buyers. Needs some updates but great bones.',
                'property_type': 'house',
                'listing_type': 'sale',
                'price': Decimal('1800000'),
                'address': 'Mekanisa, Addis Ababa',
                'city': 'Addis Ababa',
                'sub_city': 'Nifas Silk-Lafto',
                'kebele': '07',
                'country': 'Ethiopia',
                'latitude': Decimal('8.9850'),
                'longitude': Decimal('38.7250'),
                'bedrooms': 2,
                'bathrooms': Decimal('1.0'),
                'area_sqm': 120,
                'year_built': 2015,
                'status': 'active',
                'images': [
                    {'url': 'https://images.pexels.com/photos/280222/pexels-photo-280222.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Starter home'},
                    {'url': 'https://images.pexels.com/photos/1648776/pexels-photo-1648776.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Affordable option'},
                ],
            },
            {
                'title': 'Executive Apartment in Mexico',
                'description': 'Sophisticated 2-bedroom apartment in diplomatic area. Secure building with underground parking.',
                'property_type': 'apartment',
                'listing_type': 'rent',
                'price': Decimal('28000'),
                'address': 'Mexico, Addis Ababa',
                'city': 'Addis Ababa',
                'sub_city': 'Kirkos',
                'kebele': '14',
                'country': 'Ethiopia',
                'latitude': Decimal('9.0120'),
                'longitude': Decimal('38.7480'),
                'bedrooms': 2,
                'bathrooms': Decimal('2.0'),
                'area_sqm': 110,
                'year_built': 2021,
                'is_furnished': True,
                'has_air_conditioning': True,
                'has_balcony': True,
                'status': 'active',
                'images': [
                    {'url': 'https://images.pexels.com/photos/1457847/pexels-photo-1457847.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Executive apartment'},
                    {'url': 'https://images.pexels.com/photos/1329711/pexels-photo-1329711.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Professional living'},
                ],
            },
            {
                'title': 'Duplex Townhouse in Jemo',
                'description': '4-bedroom duplex townhouse with private rooftop terrace. Modern design with energy-efficient features.',
                'property_type': 'townhouse',
                'listing_type': 'sale',
                'price': Decimal('4500000'),
                'address': 'Jemo, Addis Ababa',
                'city': 'Addis Ababa',
                'sub_city': 'Akaki Kality',
                'kebele': '08',
                'country': 'Ethiopia',
                'latitude': Decimal('8.9700'),
                'longitude': Decimal('38.7600'),
                'bedrooms': 4,
                'bathrooms': Decimal('3.5'),
                'area_sqm': 260,
                'year_built': 2022,
                'has_garage': True,
                'has_balcony': True,
                'is_featured': False,
                'status': 'active',
                'images': [
                    {'url': 'https://images.pexels.com/photos/1438832/pexels-photo-1438832.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Duplex townhouse'},
                    {'url': 'https://images.pexels.com/photos/1396122/pexels-photo-1396122.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Modern design'},
                ],
            },
            {
                'title': 'Boutique Office in Meskel Flower',
                'description': 'Charming 80sqm office space perfect for startups or small businesses. Includes meeting room and kitchenette.',
                'property_type': 'commercial',
                'listing_type': 'rent',
                'price': Decimal('18000'),
                'address': 'Meskel Flower, Addis Ababa',
                'city': 'Addis Ababa',
                'sub_city': 'Bole',
                'kebele': '17',
                'country': 'Ethiopia',
                'latitude': Decimal('9.0080'),
                'longitude': Decimal('38.7550'),
                'bedrooms': 0,
                'bathrooms': Decimal('1.0'),
                'area_sqm': 80,
                'year_built': 2020,
                'has_air_conditioning': True,
                'status': 'active',
                'images': [
                    {'url': 'https://images.pexels.com/photos/380768/pexels-photo-380768.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Boutique office'},
                    {'url': 'https://images.pexels.com/photos/1181406/pexels-photo-1181406.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Creative workspace'},
                ],
            },
            {
                'title': 'Garden Apartment in Gotera',
                'description': 'Ground floor 2-bedroom apartment with private garden access. Pet-friendly building.',
                'property_type': 'apartment',
                'listing_type': 'rent',
                'price': Decimal('16000'),
                'address': 'Gotera, Addis Ababa',
                'city': 'Addis Ababa',
                'sub_city': 'Yeka',
                'kebele': '09',
                'country': 'Ethiopia',
                'latitude': Decimal('9.0350'),
                'longitude': Decimal('38.7900'),
                'bedrooms': 2,
                'bathrooms': Decimal('1.5'),
                'area_sqm': 95,
                'year_built': 2018,
                'has_garden': True,
                'status': 'active',
                'images': [
                    {'url': 'https://images.pexels.com/photos/271795/pexels-photo-271795.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Garden apartment'},
                    {'url': 'https://images.pexels.com/photos/1396122/pexels-photo-1396122.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': 'Private garden'},
                ],
            },
        ]
        
        properties_created = 0
        properties_updated = 0
        
        for prop_data in sample_properties:
            prop_payload = prop_data.copy()
            images_payload = prop_payload.pop('images', [])

            area = prop_payload.get('area_sqm') or 0
            if area:
                prop_payload['price_per_sqm'] = (prop_payload['price'] / Decimal(area)).quantize(Decimal('0.01'))

            # Use get_or_create with title to avoid duplicates
            # This ensures we never overwrite user-created properties
            # CRITICAL: Only create/update sample properties, NEVER touch user-created properties
            # Check if this is a sample property (owned by the sample agent)
            property_obj, created = Property.objects.get_or_create(
                title=prop_payload['title'],
                defaults={**prop_payload, 'owner': agent_user, 'is_published': True, 'is_active': True},
            )

            # Only update if this property is owned by the sample agent (not a user-created property)
            is_sample_property = property_obj.owner == agent_user

            if created:
                self.stdout.write(f'✅ Created sample property: {prop_payload["title"]}')
                properties_created += 1
                # For newly created sample properties, add images
                for order, image_entry in enumerate(images_payload):
                    PropertyImage.objects.create(
                        property=property_obj,
                        image=image_entry['url'],
                        caption=image_entry.get('caption'),
                        is_primary=(order == 0),
                        order=order,
                    )
            elif is_sample_property:
                # Only update sample properties (owned by agent_user), never user-created properties
                for field, value in prop_payload.items():
                    setattr(property_obj, field, value)
                property_obj.owner = agent_user
                property_obj.is_published = True
                property_obj.is_active = True
                property_obj.save()
                self.stdout.write(f'🔄 Updated sample property: {prop_payload["title"]}')
                properties_updated += 1
                
                # Only refresh images for sample properties
                PropertyImage.objects.filter(property=property_obj).delete()
                for order, image_entry in enumerate(images_payload):
                    PropertyImage.objects.create(
                        property=property_obj,
                        image=image_entry['url'],
                        caption=image_entry.get('caption'),
                        is_primary=(order == 0),
                        order=order,
                    )
            else:
                # This is a user-created property - DO NOT MODIFY IT
                self.stdout.write(f'⏭️ Skipping user-created property: {prop_payload["title"]} (owned by {property_obj.owner.username})')
                continue
        
        cache.clear()
        self.stdout.write('🧹 Cache cleared to reflect latest property data')
        self.stdout.write(f'🎉 Successfully created {properties_created} new properties!')
        self.stdout.write(f'🔄 Updated {properties_updated} existing properties!')
        self.stdout.write(f'📊 Total properties in database: {Property.objects.count()}')
        self.stdout.write(f'⭐ Featured properties: {Property.objects.filter(is_featured=True).count()}')
        self.stdout.write(f'🏠 Active properties: {Property.objects.filter(is_active=True).count()}')
        self.stdout.write(f'🏘️ Property types: Houses({Property.objects.filter(property_type="house").count()}), Apartments({Property.objects.filter(property_type="apartment").count()}), Condos({Property.objects.filter(property_type="condo").count()}), Townhouses({Property.objects.filter(property_type="townhouse").count()}), Land({Property.objects.filter(property_type="land").count()}), Commercial({Property.objects.filter(property_type="commercial").count()})')
