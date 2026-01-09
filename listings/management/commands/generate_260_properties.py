"""
Helper script to generate 260 diverse property listings with contact info
This will be integrated into populate_sample_data.py
"""

import random
from decimal import Decimal

# Ethiopian names for contact info
ETHIOPIAN_NAMES = [
    "Abebe", "Tigist", "Mulugeta", "Hirut", "Yonas", "Marta", "Solomon", "Alemitu",
    "Getachew", "Meron", "Daniel", "Selam", "Tewodros", "Rahel", "Kebede", "Mihret",
    "Bereket", "Eyerusalem", "Henok", "Bethelhem", "Yared", "Meskel", "Fitsum", "Hanna",
    "Girma", "Tsehay", "Mekonnen", "Aster", "Assefa", "Tigist", "Yohannes", "Mulu",
    "Tesfaye", "Kidan", "Amanuel", "Lydia", "Abel", "Marta", "Samuel", "Ruth",
    "Elias", "Martha", "Joseph", "Sarah", "Michael", "Mary", "David", "Esther"
]

# Phone number prefixes
PHONE_PREFIXES = ["+251911", "+251912", "+251913", "+251914", "+251915", "+251916", "+251917", "+251918", "+251919", "+251966", "+251967", "+251968", "+251969"]

# Sub-cities in Addis Ababa
SUB_CITIES = ["Bole", "Kirkos", "Arada", "Addis Ketema", "Lideta", "Nifas Silk-Lafto", "Kolfe Keranio", "Gulele", "Yeka", "Akaki Kality"]

# Property types distribution
PROPERTY_TYPES = ["house", "apartment", "condo", "townhouse", "land", "commercial"]
PROPERTY_WEIGHTS = [0.30, 0.30, 0.15, 0.10, 0.10, 0.05]  # 30% houses, 30% apartments, etc.

# Listing types
LISTING_TYPES = ["sale", "rent"]

# Price ranges by property type (in ETB)
PRICE_RANGES = {
    "house": {"sale": (1500000, 12000000), "rent": (15000, 80000)},
    "apartment": {"sale": (800000, 8000000), "rent": (8000, 50000)},
    "condo": {"sale": (1200000, 6000000), "rent": (12000, 45000)},
    "townhouse": {"sale": (2000000, 5000000), "rent": (18000, 40000)},
    "land": {"sale": (500000, 8000000), "rent": (5000, 30000)},
    "commercial": {"sale": (2000000, 15000000), "rent": (20000, 100000)}
}

# Bedroom counts by property type
BEDROOM_RANGES = {
    "house": (2, 6),
    "apartment": (1, 4),
    "condo": (1, 4),
    "townhouse": (2, 5),
    "land": (0, 0),
    "commercial": (0, 0)
}

# Area ranges by property type (sqm)
AREA_RANGES = {
    "house": (120, 500),
    "apartment": (45, 200),
    "condo": (60, 180),
    "townhouse": (100, 300),
    "land": (200, 2000),
    "commercial": (50, 1000)
}

# Pexels image IDs for different property types
IMAGE_SETS = {
    "house": [
        "1396122", "186077", "280229", "1029599", "2635038", "1571460", "1643383",
        "1648776", "1438832", "1571468", "280222", "1396132", "259588"
    ],
    "apartment": [
        "1457842", "271624", "271795", "1457847", "1329711", "439227", "1918291",
        "1643383", "1571460", "271643", "1457846", "1329712"
    ],
    "condo": [
        "1643383", "1571463", "1350789", "259962", "271643", "1457842", "271624"
    ],
    "townhouse": [
        "1438832", "1396122", "259588", "1571468", "1396132", "1438833"
    ],
    "land": [
        "1105766", "1268871", "1179229", "1105767", "1268872"
    ],
    "commercial": [
        "380768", "1181406", "1643389", "3184299", "1267338", "1267360", "1181407"
    ]
}

def generate_phone_number():
    """Generate a random Ethiopian phone number"""
    prefix = random.choice(PHONE_PREFIXES)
    suffix = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    return f"{prefix}{suffix}"

def generate_contact_info():
    """Generate random contact name and phone"""
    first_name = random.choice(ETHIOPIAN_NAMES)
    last_name = random.choice(ETHIOPIAN_NAMES)
    return {
        "contact_name": f"{first_name} {last_name}",
        "contact_phone": generate_phone_number()
    }

def generate_coordinates(sub_city):
    """Generate approximate coordinates for sub-city"""
    base_coords = {
        "Bole": (9.015, 38.760),
        "Kirkos": (9.010, 38.750),
        "Arada": (9.030, 38.740),
        "Addis Ketema": (9.005, 38.720),
        "Lideta": (9.028, 38.738),
        "Nifas Silk-Lafto": (8.985, 38.725),
        "Kolfe Keranio": (9.009, 38.739),
        "Gulele": (9.045, 38.720),
        "Yeka": (9.025, 38.785),
        "Akaki Kality": (8.950, 38.740)
    }
    base_lat, base_lng = base_coords.get(sub_city, (9.010, 38.750))
    # Add small random offset
    lat = Decimal(str(base_lat + random.uniform(-0.01, 0.01)))
    lng = Decimal(str(base_lng + random.uniform(-0.01, 0.01)))
    return lat, lng

def generate_property_images(property_type, count=3):
    """Generate image URLs from Pexels"""
    image_ids = IMAGE_SETS.get(property_type, IMAGE_SETS["house"])
    selected = random.sample(image_ids, min(count, len(image_ids)))
    images = []
    for idx, img_id in enumerate(selected):
        images.append({
            'url': f'https://images.pexels.com/photos/{img_id}/pexels-photo-{img_id}.jpeg?auto=compress&cs=tinysrgb&w=1200',
            'caption': f'{property_type.capitalize()} image {idx + 1}'
        })
    return images

def generate_property(index):
    """Generate a single property with all details"""
    # Select property type with weighted distribution
    property_type = random.choices(PROPERTY_TYPES, weights=PROPERTY_WEIGHTS)[0]
    listing_type = random.choice(LISTING_TYPES)
    sub_city = random.choice(SUB_CITIES)
    
    # Generate price based on type and listing type
    price_min, price_max = PRICE_RANGES[property_type][listing_type]
    price = Decimal(str(random.randint(price_min, price_max)))
    
    # Generate bedrooms and area
    if property_type in ["land", "commercial"]:
        bedrooms = 0
        bathrooms = Decimal('0')
    else:
        bedrooms = random.randint(*BEDROOM_RANGES[property_type])
        bathrooms = Decimal(str(random.choice([1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0])))
    
    area_sqm = random.randint(*AREA_RANGES[property_type])
    if property_type == "land":
        lot_size_sqm = area_sqm
    else:
        lot_size_sqm = None
    
    # Generate coordinates
    lat, lng = generate_coordinates(sub_city)
    
    # Generate contact info
    contact = generate_contact_info()
    
    # Property features
    has_garage = random.choice([True, False]) if property_type != "apartment" else random.choice([True, False, False])
    has_pool = random.choice([True, False, False]) if property_type in ["house", "condo"] else False
    has_garden = random.choice([True, False]) if property_type in ["house", "townhouse", "land"] else False
    has_balcony = random.choice([True, False]) if property_type in ["apartment", "condo", "townhouse"] else False
    is_furnished = random.choice([True, False]) if listing_type == "rent" else random.choice([True, False, False])
    has_air_conditioning = random.choice([True, False])
    has_heating = random.choice([True, False, False])
    
    # Year built
    year_built = random.randint(2010, 2024) if property_type != "land" else None
    
    # Generate title
    property_titles = {
        "house": [
            f"Beautiful {bedrooms}-Bedroom House in {sub_city}",
            f"Modern Family Home in {sub_city}",
            f"Spacious {bedrooms}-BR House in {sub_city}",
            f"Luxury {bedrooms}-Bedroom Villa in {sub_city}",
            f"Charming {bedrooms}-BR Home in {sub_city}"
        ],
        "apartment": [
            f"Cozy {bedrooms}-Bedroom Apartment in {sub_city}",
            f"Modern {bedrooms}-BR Apartment in {sub_city}",
            f"Luxury {bedrooms}-Bedroom Apartment in {sub_city}",
            f"Spacious {bedrooms}-BR Apartment in {sub_city}",
            f"Stylish {bedrooms}-Bedroom Apartment in {sub_city}"
        ],
        "condo": [
            f"Elegant {bedrooms}-Bedroom Condo in {sub_city}",
            f"Modern {bedrooms}-BR Condo in {sub_city}",
            f"Luxury {bedrooms}-Bedroom Condo in {sub_city}"
        ],
        "townhouse": [
            f"Modern {bedrooms}-Bedroom Townhouse in {sub_city}",
            f"Spacious {bedrooms}-BR Townhouse in {sub_city}",
            f"Luxury {bedrooms}-Bedroom Townhouse in {sub_city}"
        ],
        "land": [
            f"Prime Land Plot in {sub_city}",
            f"Development Land in {sub_city}",
            f"Investment Land in {sub_city}",
            f"Residential Land in {sub_city}"
        ],
        "commercial": [
            f"Prime Commercial Space in {sub_city}",
            f"Office Space in {sub_city}",
            f"Retail Space in {sub_city}",
            f"Warehouse in {sub_city}"
        ]
    }
    
    title = random.choice(property_titles[property_type])
    if property_type not in ["land", "commercial"]:
        title = title.replace("{bedrooms}", str(bedrooms)).replace("{BR}", f"{bedrooms}BR")
    
    # Generate description
    descriptions = {
        "house": f"Beautiful {bedrooms}-bedroom {property_type} in {sub_city}. Perfect for families with modern amenities and great location.",
        "apartment": f"Modern {bedrooms}-bedroom {property_type} in {sub_city}. Close to amenities, schools, and shopping centers.",
        "condo": f"Elegant {bedrooms}-bedroom {property_type} in {sub_city}. Building features include security and modern facilities.",
        "townhouse": f"Spacious {bedrooms}-bedroom {property_type} in {sub_city}. Great for families seeking privacy and community.",
        "land": f"Prime {area_sqm}sqm land plot in {sub_city}. Perfect for development or investment. Road access and utilities available.",
        "commercial": f"Excellent commercial space in {sub_city}. {area_sqm}sqm of prime retail/office space in high-traffic area."
    }
    description = descriptions[property_type]
    
    # Generate address
    street_names = ["Main Street", "Churchill Road", "Ras Abebe Aregay Street", "Ethiopia Street", "Unity Road"]
    street = random.choice(street_names)
    house_num = random.randint(1, 999)
    address = f"{house_num} {street}, {sub_city}, Addis Ababa"
    
    # Kebele
    kebele = str(random.randint(1, 20))
    
    # Featured property (10% chance)
    is_featured = random.random() < 0.10
    
    property_data = {
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
        'contact_name': contact['contact_name'],
        'contact_phone': contact['contact_phone'],
        'images': generate_property_images(property_type, random.randint(2, 4))
    }
    
    if lot_size_sqm:
        property_data['lot_size_sqm'] = lot_size_sqm
    
    return property_data

def generate_260_properties():
    """Generate 260 diverse properties"""
    properties = []
    for i in range(260):
        properties.append(generate_property(i))
    return properties
