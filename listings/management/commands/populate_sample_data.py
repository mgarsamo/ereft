from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from listings.models import Property, PropertyImage, Neighborhood, UserProfile
from decimal import Decimal
from django.core.cache import cache
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Populate database with comprehensive sample property data'

    def _generate_260_properties(self):
        """Generate 500 diverse properties with contact info (function name kept for compatibility)"""
        ethiopian_names = [
            "Abebe", "Tigist", "Mulugeta", "Hirut", "Yonas", "Marta", "Solomon", "Alemitu",
            "Getachew", "Meron", "Daniel", "Selam", "Tewodros", "Rahel", "Kebede", "Mihret",
            "Bereket", "Eyerusalem", "Henok", "Bethelhem", "Yared", "Meskel", "Fitsum", "Hanna",
            "Girma", "Tsehay", "Mekonnen", "Aster", "Assefa", "Yohannes", "Mulu",
            "Tesfaye", "Kidan", "Amanuel", "Lydia", "Abel", "Samuel", "Ruth",
            "Elias", "Martha", "Joseph", "Sarah", "Michael", "Mary", "David", "Esther"
        ]
        
        phone_prefixes = ["+251911", "+251912", "+251913", "+251914", "+251915", "+251916", "+251917", "+251918", "+251919", "+251966", "+251967", "+251968", "+251969"]
        sub_cities = ["Bole", "Kirkos", "Arada", "Addis Ketema", "Lideta", "Nifas Silk-Lafto", "Kolfe Keranio", "Gulele", "Yeka", "Akaki Kality"]
        property_types = ["house", "apartment", "condo", "townhouse", "land", "commercial"]
        # Better stratification: 35% houses, 35% apartments, 12% condos, 8% townhouses, 7% land, 3% commercial
        property_weights = [0.35, 0.35, 0.12, 0.08, 0.07, 0.03]
        listing_types = ["sale", "rent"]
        # Better mix: 60% for sale, 40% for rent
        listing_weights = [0.60, 0.40]
        
        price_ranges = {
            "house": {"sale": (1500000, 12000000), "rent": (15000, 80000)},
            "apartment": {"sale": (800000, 8000000), "rent": (8000, 50000)},
            "condo": {"sale": (1200000, 6000000), "rent": (12000, 45000)},
            "townhouse": {"sale": (2000000, 5000000), "rent": (18000, 40000)},
            "land": {"sale": (500000, 8000000), "rent": (5000, 30000)},
            "commercial": {"sale": (2000000, 15000000), "rent": (20000, 100000)}
        }
        
        bedroom_ranges = {
            "house": (2, 6), "apartment": (1, 4), "condo": (1, 4),
            "townhouse": (2, 5), "land": (0, 0), "commercial": (0, 0)
        }
        
        area_ranges = {
            "house": (120, 500), "apartment": (45, 200), "condo": (60, 180),
            "townhouse": (100, 300), "land": (200, 2000), "commercial": (50, 1000)
        }
        
        # Base coordinates for vacation homes (matching frontend sub-cities exactly - note: Gullele has double 'l')
        base_coords = {
            "Bole": (9.015, 38.760), 
            "CMC": (9.012, 38.755), 
            "Kirkos": (9.010, 38.750), 
            "Arada": (9.030, 38.740),
            "Lideta": (9.028, 38.738), 
            "Addis Ketema": (9.005, 38.720), 
            "Nifas Silk-Lafto": (8.985, 38.725),
            "Kolfe Keranio": (9.009, 38.739), 
            "Gullele": (9.045, 38.720),  # Double 'l' to match frontend
            "Yeka": (9.025, 38.785)
        }
        
        # Extensive image sets from Pexels for better variety
        image_sets = {
            "house": [
                "1396122", "186077", "280229", "1029599", "2635038", "1571460", "1643383", "1648776", 
                "1438832", "1571468", "280222", "1396132", "259588", "1571471", "1643384", "280233",
                "1024311", "280221", "106399", "280224", "1396138", "280223", "271743", "280225",
                "1571463", "1648768", "1396131", "1571469", "1648778", "280232", "1571470", "271724",
                "1396127", "1643385", "1571472", "280234", "271742", "1396135", "1648779", "271728",
                "1571473", "280236", "1396139", "1643386", "271729", "1571474", "280237", "271730",
                "280238", "1643387", "1571475", "280239", "271731", "1396140", "1648780", "271732"
            ],
            "apartment": [
                "1457842", "271624", "271795", "1457847", "1329711", "439227", "1918291", "1643383", 
                "1571460", "271643", "1457846", "1329712", "271796", "1457848", "271625", "271626",
                "271627", "1457849", "1329713", "271628", "271797", "1457850", "271629", "271798",
                "271630", "1457851", "1329714", "271631", "271799", "1457852", "271632", "271800",
                "271633", "1457853", "271634", "271801", "271635", "1457854", "271636", "271802",
                "271637", "1457855", "271638", "271803", "271639", "1457856", "271640", "271804",
                "1457857", "271805", "1329715", "1457858", "271806", "439228", "1457859", "271807",
                "271808", "1329716", "1457860", "271809", "439229", "1457861", "271810", "271811"
            ],
            "condo": [
                "1643383", "1571463", "1350789", "259962", "271643", "1457842", "271624", "1643384",
                "271641", "271642", "259963", "1350790", "1571464", "1643385", "271644", "271645",
                "259964", "1350791", "1571465", "1643386", "271646", "271647", "259965", "1350792",
                "1571466", "1643387", "271648", "271649", "259966", "1350793", "1571467", "1643388",
                "259967", "1350794", "271650", "1643389", "259968", "1350795", "271651", "1643390",
                "259969", "1350796", "271652", "1643391", "259970", "1350797", "271653", "1643392"
            ],
            "townhouse": [
                "1438832", "1396122", "259588", "1571468", "1396132", "1438833", "1571469", "259589",
                "1438834", "1396133", "1571470", "259590", "1438835", "1396134", "1571471", "259591",
                "1438836", "1396135", "1571472", "259592", "1438837", "1396136", "1571473", "259593",
                "1438838", "1396137", "1571474", "259594", "1438839", "1396143", "1571475", "259595",
                "1438840", "1396144", "1571476", "259596", "1438841", "1396145", "1571477", "259597"
            ],
            "land": [
                "1105766", "1268871", "1179229", "1105767", "1268872", "1105768", "1179230", "1268873",
                "1105769", "1179231", "1268874", "1105770", "1179232", "1268875", "1105771", "1179233",
                "1268876", "1105772", "1179234", "1268877", "1105773", "1179235", "1268878", "1105774",
                "1105775", "1179236", "1268879", "1105776", "1179237", "1268880", "1105777", "1179238",
                "1268881", "1105778", "1179239", "1268882", "1105779", "1179240", "1268883", "1105780"
            ],
            "commercial": [
                "380768", "1181406", "1643389", "3184299", "1267338", "1267360", "1181407", "380769",
                "1181408", "1643390", "3184300", "1267339", "1267361", "1181409", "380770", "1181410",
                "1643391", "3184301", "1267340", "1267362", "1181411", "380771", "1181412", "1643392",
                "3184302", "1267341", "1267363", "1181413", "380772", "1181414", "1643393", "3184303",
                "1181415", "1643394", "3184304", "1267342", "1267364", "1181416", "380773", "1181417",
                "1643395", "3184305", "1267343", "1267365", "1181418", "380774", "1181419", "1643396"
            ]
        }
        
        properties = []
        # Generate 500 more properties for better coverage with improved stratification
        for i in range(500):
            property_type = random.choices(property_types, weights=property_weights)[0]
            listing_type = random.choices(listing_types, weights=listing_weights)[0]
            # Ensure better geographic distribution - weighted by popularity
            city_weights = [0.25, 0.15, 0.12, 0.10, 0.10, 0.10, 0.08, 0.05, 0.03, 0.02]  # Bole most popular, etc.
            sub_city = random.choices(sub_cities, weights=city_weights)[0]
            
            price_min, price_max = price_ranges[property_type][listing_type]
            price = Decimal(str(random.randint(price_min, price_max)))
            
            if property_type in ["land", "commercial"]:
                bedrooms = 0
                bathrooms = Decimal('0')
            else:
                bedrooms = random.randint(*bedroom_ranges[property_type])
                bathrooms = Decimal(str(random.choice([1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0])))
            
            area_sqm = random.randint(*area_ranges[property_type])
            
            base_lat, base_lng = base_coords.get(sub_city, (9.010, 38.750))
            lat = Decimal(str(base_lat + random.uniform(-0.01, 0.01)))
            lng = Decimal(str(base_lng + random.uniform(-0.01, 0.01)))
            
            first_name = random.choice(ethiopian_names)
            last_name = random.choice(ethiopian_names)
            contact_name = f"{first_name} {last_name}"
            prefix = random.choice(phone_prefixes)
            contact_phone = f"{prefix}{''.join([str(random.randint(0, 9)) for _ in range(6)])}"
            
            image_ids = image_sets.get(property_type, image_sets["house"])
            # Select 3-5 images for better visual appeal
            num_images = random.randint(3, min(5, len(image_ids)))
            selected = random.sample(image_ids, num_images)
            images = [{'url': f'https://images.pexels.com/photos/{img_id}/pexels-photo-{img_id}.jpeg?auto=compress&cs=tinysrgb&w=1200', 'caption': f'{property_type.capitalize()} view {idx+1}'} for idx, img_id in enumerate(selected)]
            
            has_garage = random.choice([True, False]) if property_type != "apartment" else random.choice([True, False, False])
            has_pool = random.choice([True, False, False]) if property_type in ["house", "condo"] else False
            has_garden = random.choice([True, False]) if property_type in ["house", "townhouse", "land"] else False
            has_balcony = random.choice([True, False]) if property_type in ["apartment", "condo", "townhouse"] else False
            is_furnished = random.choice([True, False]) if listing_type == "rent" else random.choice([True, False, False])
            has_air_conditioning = random.choice([True, False])
            has_heating = random.choice([True, False, False])
            year_built = random.randint(2010, 2024) if property_type != "land" else None
            
            # More diverse title generation for better SEO and appeal
            if property_type == "house":
                title_templates = [
                    f"Beautiful {bedrooms}-Bedroom House in {sub_city}",
                    f"Modern Family Home in {sub_city}",
                    f"Spacious {bedrooms}-BR House in {sub_city}",
                    f"Luxury {bedrooms}-Bedroom Villa in {sub_city}",
                    f"Charming {bedrooms}-BR Home in {sub_city}",
                    f"Elegant {bedrooms}-Bedroom Residence in {sub_city}",
                    f"Stunning {bedrooms}-BR Family Home in {sub_city}",
                    f"Premium {bedrooms}-Bedroom Property in {sub_city}",
                    f"Contemporary {bedrooms}-BR House in {sub_city}",
                    f"Exquisite {bedrooms}-Bedroom Home in {sub_city}"
                ]
                title = random.choice(title_templates)
            elif property_type == "apartment":
                title_templates = [
                    f"Cozy {bedrooms}-Bedroom Apartment in {sub_city}",
                    f"Modern {bedrooms}-BR Apartment in {sub_city}",
                    f"Luxury {bedrooms}-Bedroom Apartment in {sub_city}",
                    f"Spacious {bedrooms}-BR Apartment in {sub_city}",
                    f"Stylish {bedrooms}-Bedroom Unit in {sub_city}",
                    f"Contemporary {bedrooms}-BR Apartment in {sub_city}",
                    f"Elegant {bedrooms}-Bedroom Flat in {sub_city}",
                    f"Premium {bedrooms}-BR Apartment in {sub_city}",
                    f"Comfortable {bedrooms}-Bedroom Apartment in {sub_city}",
                    f"Bright {bedrooms}-BR Apartment in {sub_city}"
                ]
                title = random.choice(title_templates)
            elif property_type == "condo":
                title_templates = [
                    f"Elegant {bedrooms}-Bedroom Condo in {sub_city}",
                    f"Modern {bedrooms}-BR Condo in {sub_city}",
                    f"Luxury {bedrooms}-Bedroom Condo in {sub_city}",
                    f"Stylish {bedrooms}-BR Condo in {sub_city}",
                    f"Premium {bedrooms}-Bedroom Condo in {sub_city}",
                    f"Contemporary {bedrooms}-BR Condo in {sub_city}"
                ]
                title = random.choice(title_templates)
            elif property_type == "townhouse":
                title_templates = [
                    f"Modern {bedrooms}-Bedroom Townhouse in {sub_city}",
                    f"Spacious {bedrooms}-BR Townhouse in {sub_city}",
                    f"Elegant {bedrooms}-Bedroom Townhouse in {sub_city}",
                    f"Contemporary {bedrooms}-BR Townhouse in {sub_city}",
                    f"Luxury {bedrooms}-Bedroom Townhouse in {sub_city}"
                ]
                title = random.choice(title_templates)
            elif property_type == "land":
                title_templates = [
                    f"Prime Land Plot in {sub_city}",
                    f"Development Land in {sub_city}",
                    f"Investment Land in {sub_city}",
                    f"Residential Land Plot in {sub_city}",
                    f"Buildable Land in {sub_city}",
                    f"Prime Real Estate Land in {sub_city}",
                    f"Strategic Land Location in {sub_city}",
                    f"Premium Land Parcel in {sub_city}"
                ]
                title = random.choice(title_templates)
            else:  # commercial
                title_templates = [
                    f"Prime Commercial Space in {sub_city}",
                    f"Office Space in {sub_city}",
                    f"Retail Space in {sub_city}",
                    f"Commercial Property in {sub_city}",
                    f"Business Space in {sub_city}",
                    f"Prime Storefront in {sub_city}",
                    f"Professional Office Space in {sub_city}",
                    f"Commercial Building in {sub_city}"
                ]
                title = random.choice(title_templates)
            
            # More detailed and varied descriptions
            if property_type == "house":
                desc_options = [
                    f"Beautiful {bedrooms}-bedroom house in {sub_city}. Perfect for families with modern amenities and great location.",
                    f"Stunning {bedrooms}-bedroom family home in {sub_city}. Features include spacious living areas, modern kitchen, and private garden.",
                    f"Elegant {bedrooms}-bedroom residence in {sub_city}. Well-maintained property with excellent security and prime location.",
                    f"Contemporary {bedrooms}-bedroom home in {sub_city}. Close to schools, shopping, and transportation hubs.",
                    f"Premium {bedrooms}-bedroom house in {sub_city}. Perfect investment opportunity or family residence."
                ]
                description = random.choice(desc_options)
            elif property_type == "apartment":
                desc_options = [
                    f"Modern {bedrooms}-bedroom apartment in {sub_city}. Close to amenities, schools, and shopping centers.",
                    f"Cozy {bedrooms}-bedroom unit in {sub_city}. Well-lit spaces with modern finishes and great building amenities.",
                    f"Stylish {bedrooms}-bedroom apartment in {sub_city}. Secure building with parking and excellent location.",
                    f"Spacious {bedrooms}-bedroom flat in {sub_city}. Perfect for professionals or small families.",
                    f"Bright {bedrooms}-bedroom apartment in {sub_city}. Recently renovated with quality finishes."
                ]
                description = random.choice(desc_options)
            elif property_type == "condo":
                desc_options = [
                    f"Elegant {bedrooms}-bedroom condo in {sub_city}. Building features include security, gym, and modern facilities.",
                    f"Luxury {bedrooms}-bedroom condominium in {sub_city}. High-end finishes and premium building amenities.",
                    f"Contemporary {bedrooms}-bedroom condo in {sub_city}. Secure building with excellent location and views."
                ]
                description = random.choice(desc_options)
            elif property_type == "townhouse":
                desc_options = [
                    f"Spacious {bedrooms}-bedroom townhouse in {sub_city}. Great for families seeking privacy and community living.",
                    f"Modern {bedrooms}-bedroom townhome in {sub_city}. Private parking and garden area included.",
                    f"Elegant {bedrooms}-bedroom townhouse in {sub_city}. Well-designed layout with excellent natural light."
                ]
                description = random.choice(desc_options)
            elif property_type == "land":
                desc_options = [
                    f"Prime {area_sqm}sqm land plot in {sub_city}. Perfect for development or investment. Road access and utilities available.",
                    f"Excellent {area_sqm}sqm development land in {sub_city}. Strategic location with great investment potential.",
                    f"Buildable {area_sqm}sqm land parcel in {sub_city}. All permits in place, ready for construction.",
                    f"Investment land plot in {sub_city}. {area_sqm}sqm of prime real estate with excellent growth potential."
                ]
                description = random.choice(desc_options)
            else:  # commercial
                desc_options = [
                    f"Excellent commercial space in {sub_city}. {area_sqm}sqm of prime retail/office space in high-traffic area.",
                    f"Prime commercial property in {sub_city}. {area_sqm}sqm ideal for retail, office, or restaurant use.",
                    f"Strategic commercial location in {sub_city}. {area_sqm}sqm space perfect for business establishment.",
                    f"Premium commercial space in {sub_city}. {area_sqm}sqm with excellent visibility and accessibility."
                ]
                description = random.choice(desc_options)
            
            # More diverse street names for realism
            street_names = [
                "Main Street", "Churchill Road", "Ras Abebe Aregay Street", "Ethiopia Street", "Unity Road",
                "Hailu Street", "Meskel Square", "Ras Desta Damtew Avenue", "Bole Road", "Airport Road",
                "22 Mazoria", "Cazanchise", "Gerji", "CMC Road", "Gotera", "Kazanchis", "La Gare", "Piazza",
                "Saris", "Wollo Sefer", "Megenagna", "Sar Bet", "Hayahulet", "Bole Bulbula", "Lebu", "Old Airport"
            ]
            street = random.choice(street_names)
            house_num = random.randint(1, 999)
            address = f"{house_num} {street}, {sub_city}, Addis Ababa"
            kebele = str(random.randint(1, 20))
            # Featured properties: 8% chance (good distribution but not too many)
            is_featured = random.random() < 0.08
            
            prop_data = {
                'title': title,
                'description': description,
                'property_type': property_type,
                'listing_type': listing_type,
                'price': price,
                'address': address,
                'city': 'Addis Ababa',
                'sub_city': sub_city,
                'kebele': kebele,
                'country': 'Ethiopia',
                'latitude': lat,
                'longitude': lng,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'area_sqm': area_sqm,
                'year_built': year_built,
                'has_garage': has_garage,
                'has_pool': has_pool,
                'has_garden': has_garden,
                'has_balcony': has_balcony,
                'is_furnished': is_furnished,
                'has_air_conditioning': has_air_conditioning,
                'has_heating': has_heating,
                'is_featured': is_featured,
                'status': 'active',
                'contact_name': contact_name,
                'contact_phone': contact_phone,
                'images': images
            }
            
            if property_type == "land":
                prop_data['lot_size_sqm'] = area_sqm
            
            properties.append(prop_data)
        
        return properties

    def _generate_vacation_homes(self):
        """Generate vacation home properties across all Addis Ababa sub-cities"""
        ethiopian_names = [
            "Abebe", "Tigist", "Mulugeta", "Hirut", "Yonas", "Marta", "Solomon", "Alemitu",
            "Getachew", "Meron", "Daniel", "Selam", "Tewodros", "Rahel", "Kebede", "Mihret",
            "Bereket", "Eyerusalem", "Henok", "Bethelhem", "Yared", "Meskel", "Fitsum", "Hanna",
            "Girma", "Tsehay", "Mekonnen", "Aster", "Assefa", "Yohannes", "Mulu",
            "Tesfaye", "Kidan", "Amanuel", "Lydia", "Abel", "Samuel", "Ruth",
            "Elias", "Martha", "Joseph", "Sarah", "Michael", "Mary", "David", "Esther"
        ]
        
        phone_prefixes = ["+251911", "+251912", "+251913", "+251914", "+251915", "+251916", "+251917", "+251918", "+251919", "+251966", "+251967", "+251968", "+251969"]
        
        # All Addis Ababa sub-cities for vacation homes (matching frontend list exactly)
        sub_cities = ["Bole", "CMC", "Kirkos", "Arada", "Lideta", "Addis Ketema", 
                     "Nifas Silk-Lafto", "Kolfe Keranio", "Gullele", "Yeka"]
        
        # Vacation home property images (property-only, no human pictures)
        # Using house/villa images that work well for vacation rentals
        vacation_home_images = [
            "1396122", "186077", "280229", "1029599", "2635038", "1571460", "1643383", "1648776",
            "1438832", "1571468", "280222", "1396132", "259588", "1571471", "1643384", "280233",
            "1024311", "280221", "106399", "280224", "1396138", "280223", "271743", "280225",
            "1571463", "1648768", "1396131", "1571469", "1648778", "280232", "1571470", "271724",
            "1396127", "1643385", "1571472", "280234", "271742", "1396135", "1648779", "271728",
            "271795", "1457847", "1329711", "1918291", "271643", "1457846", "1329712", "271796",
        ]
        
        # Base coordinates for vacation homes (matching frontend sub-cities exactly)
        base_coords = {
            "Bole": (9.015, 38.760), 
            "CMC": (9.012, 38.755), 
            "Kirkos": (9.010, 38.750), 
            "Arada": (9.030, 38.740),
            "Lideta": (9.028, 38.738), 
            "Addis Ketema": (9.005, 38.720), 
            "Nifas Silk-Lafto": (8.985, 38.725),
            "Kolfe Keranio": (9.009, 38.739), 
            "Gullele": (9.045, 38.720),  # Note: Double 'l' to match frontend spelling
            "Yeka": (9.025, 38.785)
        }
        
        # Vacation rental price ranges (per night in ETB)
        # Higher end vacation rentals: 25,000-100,000 per night
        # Mid-range: 15,000-50,000 per night
        price_ranges = {
            "luxury": (50000, 100000),
            "mid_range": (25000, 50000),
            "budget": (15000, 30000)
        }
        
        vacation_homes = []
        
        # Generate 50 vacation homes (5 per sub-city for good distribution)
        for sub_city in sub_cities:
            # Create 5 vacation homes per sub-city = 50 total
            for i in range(5):
                # Mix of luxury, mid-range, and budget
                price_tier = random.choice(["luxury", "mid_range", "budget", "mid_range"])  # More mid-range
                price_min, price_max = price_ranges[price_tier]
                price = Decimal(str(random.randint(price_min, price_max)))
                
                bedrooms = random.choice([2, 2, 3, 3, 4])  # Mostly 2-3 bedrooms, some 4
                bathrooms = Decimal(str(random.choice([1.0, 1.5, 2.0, 2.5, 3.0])))
                area_sqm = random.randint(100, 300)  # Vacation homes typically 100-300 sqm
                
                base_lat, base_lng = base_coords.get(sub_city, (9.010, 38.750))  # Default to Addis Ababa center if not found
                lat = Decimal(str(base_lat + random.uniform(-0.01, 0.01)))
                lng = Decimal(str(base_lng + random.uniform(-0.01, 0.01)))
                
                first_name = random.choice(ethiopian_names)
                last_name = random.choice(ethiopian_names)
                contact_name = f"{first_name} {last_name}"
                prefix = random.choice(phone_prefixes)
                contact_phone = f"{prefix}{''.join([str(random.randint(0, 9)) for _ in range(6)])}"
                
                # Select 2-4 property images (fewer images for now as requested)
                num_images = random.choice([2, 3, 4])
                selected = random.sample(vacation_home_images, min(num_images, len(vacation_home_images)))
                images = [
                    {'url': f'https://images.pexels.com/photos/{img_id}/pexels-photo-{img_id}.jpeg?auto=compress&cs=tinysrgb&w=1200', 
                     'caption': f'Vacation home view {idx+1}'} 
                    for idx, img_id in enumerate(selected)
                ]
                
                # Vacation home features
                has_pool = random.choice([True, False, False])  # 33% have pools
                has_garden = random.choice([True, True, False])  # 67% have gardens
                has_balcony = random.choice([True, True, False])  # 67% have balconies
                is_furnished = True  # Vacation homes are always furnished
                has_air_conditioning = random.choice([True, True, False])  # 67% have AC
                
                # Generate descriptive title based on features
                title_parts = []
                if price >= 70000:
                    title_parts.append("Luxury")
                elif price >= 40000:
                    title_parts.append("Premium")
                
                if has_pool:
                    title_parts.append("Pool")
                if bedrooms >= 4:
                    title_parts.append(f"{bedrooms}-Bedroom")
                elif bedrooms == 3:
                    title_parts.append("Spacious 3-Bedroom")
                else:
                    title_parts.append(f"Cozy {bedrooms}-Bedroom")
                
                title_parts.append("Vacation Home")
                title = f"{' '.join(title_parts)} in {sub_city}"
                
                description = f"Beautiful vacation rental in {sub_city}. "
                if has_pool:
                    description += "Features a private pool, "
                if has_garden:
                    description += "landscaped garden, "
                description += f"{bedrooms} bedrooms and {bathrooms} bathrooms. Fully furnished with modern amenities. "
                if has_air_conditioning:
                    description += "Air-conditioned for comfort. "
                description += f"Perfect for families or groups looking for a relaxing getaway in Addis Ababa."
                
                prop_data = {
                    'title': title,
                    'description': description,
                    'property_type': 'vacation_home',
                    'listing_type': 'rent',  # Vacation homes are always for rent
                    'price': price,
                    'address': f"{sub_city}, Addis Ababa",
                    'city': 'Addis Ababa',
                    'sub_city': sub_city,
                    'kebele': f"{random.randint(1, 15):02d}",
                    'country': 'Ethiopia',
                    'latitude': lat,
                    'longitude': lng,
                    'bedrooms': bedrooms,
                    'bathrooms': bathrooms,
                    'area_sqm': area_sqm,
                    'year_built': random.randint(2015, 2024),
                    'is_furnished': is_furnished,
                    'has_pool': has_pool,
                    'has_garden': has_garden,
                    'has_balcony': has_balcony,
                    'has_air_conditioning': has_air_conditioning,
                    'has_garage': random.choice([True, False]),
                    'status': 'active',
                    'is_featured': random.choice([True, False, False, False]),  # 25% featured
                    'contact_name': contact_name,
                    'contact_phone': contact_phone,
                    'images': images
                }
                
                vacation_homes.append(prop_data)
        
        return vacation_homes

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
        
        # Generate 500 additional diverse properties with contact info and extensive image sets
        self.stdout.write('🔄 Generating 500 additional diverse properties with extensive image coverage...')
        additional_properties = self._generate_260_properties()  # Function name is legacy, but generates 500 now
        
        # Generate vacation homes
        self.stdout.write('🏖️ Generating vacation home properties...')
        vacation_homes = self._generate_vacation_homes()
        self.stdout.write(f'   Generated {len(vacation_homes)} vacation home properties across all Addis Ababa sub-cities')
        
        # Combine all properties
        sample_properties.extend(additional_properties)
        sample_properties.extend(vacation_homes)
        self.stdout.write(f'✅ Generated {len(additional_properties)} additional properties with stratified distribution')
        self.stdout.write(f'✅ Added {len(vacation_homes)} vacation home properties')
        
        properties_created = 0
        properties_updated = 0
        
        for prop_data in sample_properties:
            prop_payload = prop_data.copy()
            images_payload = prop_payload.pop('images', [])

            area = prop_payload.get('area_sqm') or 0
            if area:
                prop_payload['price_per_sqm'] = (prop_payload['price'] / Decimal(area)).quantize(Decimal('0.01'))

            # Extract contact info if present
            contact_name = prop_payload.pop('contact_name', None)
            contact_phone = prop_payload.pop('contact_phone', None)
            
            # Use get_or_create with title to avoid duplicates
            # This ensures we never overwrite user-created properties
            # CRITICAL: Only create/update sample properties, NEVER touch user-created properties
            # Check if this is a sample property (owned by the sample agent)
            property_obj, created = Property.objects.get_or_create(
                title=prop_payload['title'],
                defaults={**prop_payload, 'owner': agent_user, 'is_published': True, 'is_active': True, 'contact_name': contact_name, 'contact_phone': contact_phone},
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
                if contact_name:
                    property_obj.contact_name = contact_name
                if contact_phone:
                    property_obj.contact_phone = contact_phone
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
        
        # Final counts
        total_properties = Property.objects.count()
        sample_properties_count = Property.objects.filter(owner=agent_user).count()
        user_properties_count = total_properties - sample_properties_count
        
        self.stdout.write('')
        self.stdout.write('=' * 60)
        self.stdout.write('SAMPLE DATA POPULATION SUMMARY')
        self.stdout.write('=' * 60)
        self.stdout.write(f'✅ Successfully created {properties_created} new sample properties!')
        self.stdout.write(f'🔄 Updated {properties_updated} existing sample properties!')
        self.stdout.write(f'⏭️  Skipped {len(sample_properties) - properties_created - properties_updated} properties (user-created, not modified)')
        self.stdout.write('')
        self.stdout.write(f'📊 Total properties in database: {total_properties}')
        self.stdout.write(f'   - Sample properties: {sample_properties_count}')
        self.stdout.write(f'   - User-created properties: {user_properties_count}')
        self.stdout.write(f'⭐ Featured properties: {Property.objects.filter(is_featured=True).count()}')
        self.stdout.write(f'🏠 Active properties: {Property.objects.filter(is_active=True).count()}')
        self.stdout.write(f'🏘️ Property types: Houses({Property.objects.filter(property_type="house").count()}), Apartments({Property.objects.filter(property_type="apartment").count()}), Condos({Property.objects.filter(property_type="condo").count()}), Townhouses({Property.objects.filter(property_type="townhouse").count()}), Vacation Homes({Property.objects.filter(property_type="vacation_home").count()}), Land({Property.objects.filter(property_type="land").count()}), Commercial({Property.objects.filter(property_type="commercial").count()})')
        self.stdout.write('=' * 60)
        
        if sample_properties_count < 20:
            self.stdout.write(f'⚠️ WARNING: Only {sample_properties_count} sample properties found. Expected ~24 properties.')
            self.stdout.write('   This might indicate an issue with property creation.')
        else:
            self.stdout.write(f'✅ Sample data population complete! {sample_properties_count} sample properties available.')
