# FILE: ereft_api/listings/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    UserProfile, Property, PropertyImage, Favorite, PropertyView,
    SearchHistory, Contact, Neighborhood, PropertyReview,
    Availability, Booking, RecurringAvailabilityRule
)

class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer"""
    phone_number = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'phone_number', 'profile_picture']
    
    def get_phone_number(self, obj):
        """Get phone number from UserProfile if it exists"""
        try:
            profile = obj.profile
            return profile.phone_number
        except UserProfile.DoesNotExist:
            return None
    
    def get_profile_picture(self, obj):
        """Get profile picture from UserProfile if it exists"""
        try:
            profile = obj.profile
            return profile.profile_picture
        except UserProfile.DoesNotExist:
            return None

class UserProfileSerializer(serializers.ModelSerializer):
    """User profile serializer"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'

class PropertyImageSerializer(serializers.ModelSerializer):
    """Property image serializer - BULLETPROOF: Always returns image_url"""
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'image_url', 'caption', 'is_primary', 'order', 'created_at']
    
    def get_image_url(self, obj):
        """BULLETPROOF: Always return full Cloudinary URL - construct from public_id or use stored URL"""
        # Removed verbose debug logging - uncomment for debugging if needed
        # print(f"🔍 PropertyImageSerializer.get_image_url: Called for PropertyImage ID={obj.id if obj else 'None'}")
        
        if not obj or not obj.image:
            # print(f"   ⚠️ No obj or no obj.image, returning None")
            return None
        
        image_value = str(obj.image).strip()
        if not image_value or image_value in ['None', 'null', '']:
            return None
        
        # CRITICAL FIX: Extract public_id from list representation if stored incorrectly
        # Handle cases where the value is stored as ['public_id'] or "[ 'public_id' ]" etc.
        import re
        import ast
        import json
        
        # Try to extract public_id from list representation
        if image_value.startswith('[') and image_value.endswith(']'):
            try:
                # Try to parse as Python list literal
                parsed_list = ast.literal_eval(image_value)
                if isinstance(parsed_list, list) and len(parsed_list) > 0:
                    image_value = str(parsed_list[0]).strip().strip("'\"")
            except (ValueError, SyntaxError):
                try:
                    # Try to parse as JSON
                    parsed_list = json.loads(image_value)
                    if isinstance(parsed_list, list) and len(parsed_list) > 0:
                        image_value = str(parsed_list[0]).strip().strip("'\"")
                except (ValueError, json.JSONDecodeError):
                    # Try regex extraction
                    match = re.search(r"['\"]([^'\"]+)['\"]", image_value)
                    if match:
                        image_value = match.group(1)
        
        # Remove any remaining quotes
        image_value = image_value.strip().strip("'\"")
        
        # If it's already a full URL (starts with http/https), return it directly
        if image_value.startswith('http://') or image_value.startswith('https://'):
            # Convert HTTP to HTTPS
            if image_value.startswith('http://'):
                image_value = image_value.replace('http://', 'https://', 1)
            return image_value
        
        # If it's a public_id (like "ereft_properties/nggejftgnzxzwuitw3wp"), construct the URL
        # Public IDs don't start with http, they're just identifiers
        if image_value and not image_value.startswith('http'):
            # CRITICAL: Validate public_id format (should not contain brackets or quotes)
            if '[' in image_value or ']' in image_value or image_value.startswith("'") or image_value.startswith('"'):
                # Try to clean it up one more time
                image_value = re.sub(r"^['\"]+|['\"]+$", "", image_value)
                image_value = re.sub(r"\[|\]", "", image_value)
                image_value = image_value.strip()
            
            # Try using Cloudinary SDK first
            try:
                from .utils import get_cloudinary_url
                cloudinary_url = get_cloudinary_url(image_value)
                if cloudinary_url:
                    return cloudinary_url
            except Exception:
                pass
            
            # Fallback: Construct URL manually
            try:
                from django.conf import settings
                cloud_name = getattr(settings, 'CLOUDINARY_CLOUD_NAME', 'detdm1snc')
                # CRITICAL: Construct full Cloudinary URL format:
                # https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}
                # Cloudinary will serve the image with the correct format automatically
                url = f"https://res.cloudinary.com/{cloud_name}/image/upload/{image_value}"
                return url
            except Exception:
                pass
        
        return None
    
    def to_representation(self, instance):
        """BULLETPROOF: Always construct full Cloudinary URL from public_id stored in image field"""
        # Removed verbose debug logging - uncomment for debugging if needed
        # print(f"🔍 PropertyImageSerializer.to_representation: Called for PropertyImage ID={instance.id if instance else 'None'}")
        
        representation = super().to_representation(instance)
        
        # CRITICAL: image field contains public_id (e.g., "ereft_properties/nggejftgnzxzwuitw3wp")
        # We need to construct the full Cloudinary URL from it
        image_url = representation.get('image_url')
        
        # If image_url is already set by get_image_url() and is a full HTTPS URL, use it
        if image_url and image_url.startswith('https://'):
            representation['image_url'] = image_url
            return representation
        
        # Otherwise, construct from image field (public_id)
        if image_field:
            # CRITICAL FIX: Extract public_id from list representation if stored incorrectly
            import re
            import ast
            import json
            
            public_id = str(image_field).strip()
            
            # Try to extract public_id from list representation (e.g., "['ereft_properties/xxx']")
            if public_id.startswith('[') and public_id.endswith(']'):
                print(f"   ⚠️ WARNING: image_field appears to be a list representation: '{public_id}'")
                try:
                    # Try to parse as Python list literal
                    parsed_list = ast.literal_eval(public_id)
                    if isinstance(parsed_list, list) and len(parsed_list) > 0:
                        public_id = str(parsed_list[0]).strip().strip("'\"")
                        print(f"   ✅ Extracted public_id from list: '{public_id}'")
                except (ValueError, SyntaxError):
                    try:
                        # Try to parse as JSON
                        parsed_list = json.loads(public_id)
                        if isinstance(parsed_list, list) and len(parsed_list) > 0:
                            public_id = str(parsed_list[0]).strip().strip("'\"")
                            print(f"   ✅ Extracted public_id from JSON list: '{public_id}'")
                    except (ValueError, json.JSONDecodeError):
                        # Try regex extraction
                        match = re.search(r"['\"]([^'\"]+)['\"]", public_id)
                        if match:
                            public_id = match.group(1)
                            print(f"   ✅ Extracted public_id using regex: '{public_id}'")
            
            # Remove any remaining quotes
            public_id = public_id.strip().strip("'\"")
            
            # Validate public_id format (should not contain brackets or quotes)
            if '[' in public_id or ']' in public_id:
                print(f"   ❌ WARNING: Invalid public_id format detected: '{public_id}'")
                # Try to clean it up one more time
                public_id = re.sub(r"\[|\]", "", public_id)
                public_id = re.sub(r"^['\"]+|['\"]+$", "", public_id)
                public_id = public_id.strip()
                print(f"   Cleaned public_id: '{public_id}'")
            
            # If it's already a full URL, use it directly
            if public_id.startswith('http://') or public_id.startswith('https://'):
                if public_id.startswith('http://'):
                    public_id = public_id.replace('http://', 'https://', 1)
                representation['image_url'] = public_id
                print(f"   ✅ image_field is already a URL: {public_id[:80]}...")
                return representation
            
            # It's a public_id - construct full Cloudinary URL
            # public_id format: "ereft_properties/nggejftgnzxzwuitw3wp"
            print(f"   Constructing URL from public_id: '{public_id}'")
            
            # Try using Cloudinary SDK first
            try:
                from .utils import get_cloudinary_url
                from django.conf import settings
                
                full_url = get_cloudinary_url(public_id)
                
                if full_url:
                    representation['image_url'] = full_url
                    print(f"   ✅ Constructed URL via SDK in to_representation: {full_url[:80]}...")
                    return representation
                else:
                    print(f"   ⚠️ get_cloudinary_url returned None in to_representation")
            except Exception as e:
                print(f"   ⚠️ Failed to use get_cloudinary_url in to_representation: {e}")
                import traceback
                traceback.print_exc()
            
            # Fallback: Construct URL manually
            try:
                from django.conf import settings
                cloud_name = getattr(settings, 'CLOUDINARY_CLOUD_NAME', 'detdm1snc')
                # CRITICAL: Construct full Cloudinary URL format:
                # https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}
                # Cloudinary will serve the image with the correct format automatically
                full_url = f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}"
                representation['image_url'] = full_url
                print(f"   ✅ Constructed URL manually in to_representation: {full_url}")
                return representation
            except Exception as e:
                print(f"   ❌ Failed to construct URL manually in to_representation: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"   ⚠️ No image_field found in representation")
        
        # FINAL FALLBACK: Ensure image_url is always set (even if we have to use None)
        if not representation.get('image_url'):
            print(f"   ⚠️ No image_url set, using None")
            representation['image_url'] = None
        
        print(f"   📤 Final representation image_url: '{representation.get('image_url', 'None')[:80] if representation.get('image_url') else 'None'}...'")
        return representation

class PropertySerializer(serializers.ModelSerializer):
    """Property serializer with nested images"""
    images = PropertyImageSerializer(many=True, read_only=True)
    owner = UserSerializer(read_only=True)
    agent = UserSerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = '__all__'
    
    def validate(self, data):
        """Validate that contact_name and contact_phone are required for updates"""
        # Only validate if this is a create/update operation (not a read)
        if self.instance is None:  # This is a create operation
            contact_name = data.get('contact_name', '').strip() if data.get('contact_name') else ''
            contact_phone = data.get('contact_phone', '').strip() if data.get('contact_phone') else ''
            
            if not contact_name:
                raise serializers.ValidationError({
                    'contact_name': 'Contact Name is required.'
                })
            
            if not contact_phone:
                raise serializers.ValidationError({
                    'contact_phone': 'Contact Phone is required.'
                })
        else:  # This is an update operation
            # For updates, validate if the fields are being updated
            contact_name = data.get('contact_name', None)
            contact_phone = data.get('contact_phone', None)
            
            # If fields are provided in the update, they must not be empty
            if 'contact_name' in data:
                contact_name_str = contact_name.strip() if contact_name else ''
                if not contact_name_str:
                    raise serializers.ValidationError({
                        'contact_name': 'Contact Name is required.'
                    })
            
            if 'contact_phone' in data:
                contact_phone_str = contact_phone.strip() if contact_phone else ''
                if not contact_phone_str:
                    raise serializers.ValidationError({
                        'contact_phone': 'Contact Phone is required.'
                    })
        
        return data
    
    def to_representation(self, instance):
        """Remove contact_name and contact_phone for non-admin users"""
        representation = super().to_representation(instance)
        request = self.context.get('request')
        
        # Check if user is admin
        is_admin = False
        if request and request.user and request.user.is_authenticated:
            is_admin = (
                request.user.is_staff or 
                request.user.is_superuser or 
                request.user.email in [
                    'admin@ereft.com', 
                    'melaku.garsamo@gmail.com', 
                    'cb.garsamo@gmail.com', 
                    'lydiageleta45@gmail.com'
                ]
            )
        
        # Remove contact info for non-admin users
        if not is_admin:
            representation.pop('contact_name', None)
            representation.pop('contact_phone', None)
        
        return representation
    
    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return PropertyImageSerializer(primary_image).data
        return None
    
    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(user=request.user).exists()
        return False

class PropertyListSerializer(serializers.ModelSerializer):
    """Simplified property serializer for list views - Ethiopia fields, m² units"""
    images = PropertyImageSerializer(many=True, read_only=True)
    owner = UserSerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = [
            'id', 'title', 'price', 'property_type', 'listing_type',
            'address', 'city', 'sub_city', 'kebele', 'bedrooms', 'bathrooms',
            'area_sqm', 'images', 'primary_image', 'is_favorited', 'created_at', 'status', 'owner', 'views_count',
            # Vacation home availability fields
            'availability_start_date', 'availability_end_date', 'min_stay_nights', 'max_stay_nights', 'booking_preference'
        ]
        # Note: contact_name and contact_phone are NOT in fields list, so they won't be included
    
    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            # Return full PropertyImageSerializer data, not just the raw image field
            return PropertyImageSerializer(primary_image).data
        return None
    
    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(user=request.user).exists()
        return False

class FlexibleCharField(serializers.CharField):
    """CharField that can handle any input type and convert to string"""
    def to_internal_value(self, data):
        """Convert any input to string"""
        if data is None:
            return None
        if isinstance(data, str):
            return data.strip()
        # Convert anything else to string
        try:
            return str(data).strip()
        except:
            raise serializers.ValidationError("Cannot convert to string")

class PropertyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating properties - Ethiopia fields, m² units"""
    images = serializers.ListField(
        child=FlexibleCharField(allow_blank=False, allow_null=False),
        required=False,
        allow_empty=True,
        allow_null=True
    )
    
    def validate_images(self, value):
        """CRITICAL: Validate images are all strings before processing"""
        print(f"🔍 PropertyCreateSerializer.validate_images: Called with value type={type(value)}")
        if not value:
            print(f"   Value is empty/None, returning []")
            return []
        
        if not isinstance(value, list):
            print(f"   ⚠️ Value is not a list! Type: {type(value)}, converting...")
            value = [value] if value else []
        
        validated_images = []
        for idx, item in enumerate(value):
            print(f"   Validating image {idx}: type={type(item).__name__}, value={str(item)[:50] if item else 'None'}...")
            
            # CRITICAL: Ensure it's a string
            if isinstance(item, str):
                item_str = item.strip()
                if item_str and len(item_str) > 5:
                    validated_images.append(item_str)
                    print(f"   ✅ Image {idx}: Valid string '{item_str[:50]}...'")
                else:
                    print(f"   ⚠️ Image {idx}: String too short or empty, skipping")
            elif item is None:
                print(f"   ⚠️ Image {idx}: None, skipping")
                continue
            elif hasattr(item, 'read'):  # File-like
                print(f"   ❌ Image {idx}: File-like object, skipping")
                continue
            else:
                # Try to convert to string
                try:
                    item_str = str(item).strip()
                    if item_str and len(item_str) > 5 and item_str not in ['None', 'null', '']:
                        validated_images.append(item_str)
                        print(f"   ✅ Image {idx}: Converted to string '{item_str[:50]}...'")
                    else:
                        print(f"   ⚠️ Image {idx}: Empty or invalid after conversion, skipping")
                except Exception as e:
                    print(f"   ❌ Image {idx}: Cannot convert to string: {e}, skipping")
                    continue
        
        print(f"✅ PropertyCreateSerializer.validate_images: Returning {len(validated_images)} validated images")
        return validated_images
    
    class Meta:
        model = Property
        fields = [
            'title', 'description', 'property_type', 'listing_type', 'price',
            'address', 'city', 'sub_city', 'kebele', 'street_name', 'house_number', 
            'country', 'latitude', 'longitude',
            'bedrooms', 'bathrooms', 'area_sqm', 'lot_size_sqm', 'year_built',
            'has_garage', 'has_pool', 'has_garden', 'has_balcony', 'is_furnished',
            'has_air_conditioning', 'has_heating', 'contact_name', 'contact_phone', 'images',
            # Vacation home specific fields
            'availability_start_date', 'availability_end_date', 'min_stay_nights', 
            'max_stay_nights', 'booking_preference', 'max_adults', 'max_children', 'pets_allowed'
        ]
    
    def validate(self, data):
        """Validate that contact_name and contact_phone are required"""
        contact_name = data.get('contact_name', '').strip() if data.get('contact_name') else ''
        contact_phone = data.get('contact_phone', '').strip() if data.get('contact_phone') else ''
        
        if not contact_name:
            raise serializers.ValidationError({
                'contact_name': 'Contact Name is required.'
            })
        
        if not contact_phone:
            raise serializers.ValidationError({
                'contact_phone': 'Contact Phone is required.'
            })
        
        # Validate vacation home specific fields if property_type is vacation_home
        if data.get('property_type') == 'vacation_home':
            if not data.get('availability_start_date'):
                raise serializers.ValidationError({
                    'availability_start_date': 'Start date is required for vacation homes.'
                })
            min_stay = data.get('min_stay_nights', 1)
            if min_stay < 1:
                raise serializers.ValidationError({
                    'min_stay_nights': 'Minimum stay must be at least 1 night.'
                })
            max_stay = data.get('max_stay_nights')
            if max_stay and max_stay < min_stay:
                raise serializers.ValidationError({
                    'max_stay_nights': 'Maximum stay cannot be less than minimum stay.'
                })
            # Force listing_type to 'rent' for vacation homes
            data['listing_type'] = 'rent'
        
        return data
    
    # Note: Property creation is handled by perform_create in views.py
    # to properly handle file uploads and image processing

class AvailabilitySerializer(serializers.ModelSerializer):
    """Serializer for Availability model"""
    property = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Availability
        fields = ['id', 'property', 'date', 'status', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking model"""
    property = serializers.PrimaryKeyRelatedField(read_only=True)
    guest = UserSerializer(read_only=True)
    property_title = serializers.CharField(source='property.title', read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'property', 'property_title', 'guest', 'guest_name', 'guest_email', 
            'guest_phone', 'check_in_date', 'check_out_date', 'nights', 'total_price',
            'message', 'status', 'is_instant_booking', 'created_at', 'updated_at',
            'confirmed_at', 'cancelled_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'confirmed_at', 'cancelled_at']

class RecurringAvailabilityRuleSerializer(serializers.ModelSerializer):
    """Serializer for RecurringAvailabilityRule model"""
    property = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = RecurringAvailabilityRule
        fields = [
            'id', 'property', 'rule_type', 'status', 'days_of_week', 'day_of_month',
            'month', 'day', 'start_date', 'end_date', 'notes', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class FavoriteSerializer(serializers.ModelSerializer):
    """Favorite serializer"""
    property = PropertyListSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Favorite
        fields = ['id', 'property', 'user', 'created_at']

class SearchHistorySerializer(serializers.ModelSerializer):
    """Search history serializer"""
    class Meta:
        model = SearchHistory
        fields = ['id', 'query', 'filters', 'created_at']

class ContactSerializer(serializers.ModelSerializer):
    """Contact form serializer"""
    class Meta:
        model = Contact
        fields = ['id', 'property', 'name', 'email', 'phone', 'message', 'contact_type', 'created_at']
        read_only_fields = ['id', 'created_at']

class NeighborhoodSerializer(serializers.ModelSerializer):
    """Neighborhood serializer"""
    class Meta:
        model = Neighborhood
        fields = '__all__'

class PropertyReviewSerializer(serializers.ModelSerializer):
    """Property review serializer"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = PropertyReview
        fields = ['id', 'property', 'user', 'rating', 'comment', 'is_verified', 'created_at']
        read_only_fields = ['id', 'user', 'is_verified', 'created_at']

class PropertyDetailSerializer(serializers.ModelSerializer):
    """Detailed property serializer with all related data"""
    images = PropertyImageSerializer(many=True, read_only=True)
    owner = UserSerializer(read_only=True)
    agent = UserSerializer(read_only=True)
    reviews = PropertyReviewSerializer(many=True, read_only=True)
    primary_image = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = '__all__'
    
    def validate(self, data):
        """Validate that contact_name and contact_phone are required for updates"""
        # Only validate if this is a create/update operation (not a read)
        if self.instance is None:  # This is a create operation
            contact_name = data.get('contact_name', '').strip() if data.get('contact_name') else ''
            contact_phone = data.get('contact_phone', '').strip() if data.get('contact_phone') else ''
            
            if not contact_name:
                raise serializers.ValidationError({
                    'contact_name': 'Contact Name is required.'
                })
            
            if not contact_phone:
                raise serializers.ValidationError({
                    'contact_phone': 'Contact Phone is required.'
                })
        else:  # This is an update operation
            # For updates, validate if the fields are being updated
            contact_name = data.get('contact_name', None)
            contact_phone = data.get('contact_phone', None)
            
            # If fields are provided in the update, they must not be empty
            if 'contact_name' in data:
                contact_name_str = contact_name.strip() if contact_name else ''
                if not contact_name_str:
                    raise serializers.ValidationError({
                        'contact_name': 'Contact Name is required.'
                    })
            
            if 'contact_phone' in data:
                contact_phone_str = contact_phone.strip() if contact_phone else ''
                if not contact_phone_str:
                    raise serializers.ValidationError({
                        'contact_phone': 'Contact Phone is required.'
                    })
        
        return data
    
    def to_representation(self, instance):
        """Remove contact_name and contact_phone for non-admin users"""
        representation = super().to_representation(instance)
        request = self.context.get('request')
        
        # Check if user is admin
        is_admin = False
        if request and request.user and request.user.is_authenticated:
            is_admin = (
                request.user.is_staff or 
                request.user.is_superuser or 
                request.user.email in [
                    'admin@ereft.com', 
                    'melaku.garsamo@gmail.com', 
                    'cb.garsamo@gmail.com', 
                    'lydiageleta45@gmail.com'
                ]
            )
        
        # Remove contact info for non-admin users
        if not is_admin:
            representation.pop('contact_name', None)
            representation.pop('contact_phone', None)
        
        return representation
    
    def get_primary_image(self, obj):
        """CRITICAL: Get primary image - must return object with full HTTPS image_url"""
        print(f"🔍 PropertyDetailSerializer.get_primary_image: Called for Property ID={obj.id if obj else 'None'}")
        
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            print(f"   Found primary image: ID={primary_image.id}, public_id='{primary_image.image[:50] if primary_image.image else 'None'}...'")
            serialized = PropertyImageSerializer(primary_image).data
            print(f"   Serialized primary_image image_url: '{serialized.get('image_url', 'None')[:80] if serialized.get('image_url') else 'None'}...'")
            
            # CRITICAL: Ensure image_url is a full HTTPS URL
            if not serialized.get('image_url') or not serialized.get('image_url', '').startswith('https://'):
                image_field = serialized.get('image')
                if image_field:
                    public_id = str(image_field).strip()
                    print(f"   Constructing image_url from image field (public_id): '{public_id[:50]}...'")
                    
                    # If it's already a URL, convert to HTTPS
                    if public_id.startswith('http://') or public_id.startswith('https://'):
                        if public_id.startswith('http://'):
                            public_id = public_id.replace('http://', 'https://', 1)
                        serialized['image_url'] = public_id
                        print(f"   ✅ Converted HTTP to HTTPS: {public_id[:80]}...")
                    else:
                        # It's a public_id - construct full URL
                        try:
                            from .utils import get_cloudinary_url
                            from django.conf import settings
                            
                            full_url = get_cloudinary_url(public_id)
                            if full_url:
                                serialized['image_url'] = full_url
                                print(f"   ✅ Constructed URL via SDK: {full_url[:80]}...")
                            else:
                                # Fallback manual construction
                                cloud_name = getattr(settings, 'CLOUDINARY_CLOUD_NAME', 'detdm1snc')
                                full_url = f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}"
                                serialized['image_url'] = full_url
                                print(f"   ✅ Constructed URL manually: {full_url[:80]}...")
                        except Exception as e:
                            print(f"   ⚠️ Failed to construct URL: {e}, using manual fallback")
                            from django.conf import settings
                            cloud_name = getattr(settings, 'CLOUDINARY_CLOUD_NAME', 'detdm1snc')
                            full_url = f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}"
                            serialized['image_url'] = full_url
                            print(f"   ✅ Used manual fallback: {full_url[:80]}...")
            
            print(f"   📤 Final primary_image image_url: '{serialized.get('image_url', 'None')[:80] if serialized.get('image_url') else 'None'}...'")
            return serialized
        else:
            # Try to get first image if no primary
            first_image = obj.images.first()
            if first_image:
                print(f"   No primary, using first image: ID={first_image.id}, public_id='{first_image.image[:50] if first_image.image else 'None'}...'")
                serialized = PropertyImageSerializer(first_image).data
                
                # CRITICAL: Ensure image_url is a full HTTPS URL
                if not serialized.get('image_url') or not serialized.get('image_url', '').startswith('https://'):
                    image_field = serialized.get('image')
                    if image_field:
                        public_id = str(image_field).strip()
                        print(f"   Constructing image_url from image field (public_id): '{public_id[:50]}...'")
                        
                        # If it's already a URL, convert to HTTPS
                        if public_id.startswith('http://') or public_id.startswith('https://'):
                            if public_id.startswith('http://'):
                                public_id = public_id.replace('http://', 'https://', 1)
                            serialized['image_url'] = public_id
                        else:
                            # It's a public_id - construct full URL
                            try:
                                from .utils import get_cloudinary_url
                                from django.conf import settings
                                
                                full_url = get_cloudinary_url(public_id)
                                if full_url:
                                    serialized['image_url'] = full_url
                                else:
                                    cloud_name = getattr(settings, 'CLOUDINARY_CLOUD_NAME', 'detdm1snc')
                                    full_url = f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}"
                                    serialized['image_url'] = full_url
                            except Exception as e:
                                from django.conf import settings
                                cloud_name = getattr(settings, 'CLOUDINARY_CLOUD_NAME', 'detdm1snc')
                                full_url = f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}"
                                serialized['image_url'] = full_url
                                print(f"   ✅ Used manual fallback: {full_url[:80]}...")
                
                print(f"   📤 Final first_image image_url: '{serialized.get('image_url', 'None')[:80] if serialized.get('image_url') else 'None'}...'")
                return serialized
        print(f"   ⚠️ No images found for property")
        return None
    
    def to_representation(self, instance):
        """CRITICAL: Ensure images are ALWAYS included with valid full HTTPS image_url"""
        print(f"🔍 PropertyDetailSerializer.to_representation: Called for Property ID={instance.id if instance else 'None'}")
        
        representation = super().to_representation(instance)
        
        # CRITICAL: Query images directly from database to ensure they're included
        db_images = list(instance.images.all().order_by('order', 'created_at')[:4])
        images_data = representation.get('images', [])
        
        print(f"   DB images count: {len(db_images)}")
        print(f"   Representation images count: {len(images_data)}")
        
        # If serializer didn't include images, add them from database
        if not images_data or len(images_data) == 0:
            if db_images:
                print(f"   ⚠️ No images in representation, adding from database...")
                representation['images'] = [PropertyImageSerializer(img).data for img in db_images]
                print(f"   ✅ Added {len(representation['images'])} images from database")
        
        # CRITICAL: Ensure every image has image_url set to a valid HTTPS URL
        if representation.get('images'):
            print(f"   Ensuring all {len(representation['images'])} images have valid HTTPS image_url...")
            for idx, img_data in enumerate(representation['images']):
                current_url = img_data.get('image_url', '')
                image_field = img_data.get('image')
                
                print(f"   Image {idx + 1}: image_url='{current_url[:80] if current_url else 'None'}...', image_field='{image_field[:50] if image_field else 'None'}...'")
                
                # If image_url is missing or not HTTPS, construct from image field (public_id)
                if not current_url or not current_url.startswith('https://'):
                    if image_field:
                        public_id = str(image_field).strip()
                        
                        # If it's already a URL, convert to HTTPS
                        if public_id.startswith('http://') or public_id.startswith('https://'):
                            if public_id.startswith('http://'):
                                public_id = public_id.replace('http://', 'https://', 1)
                            img_data['image_url'] = public_id
                            print(f"   ✅ Image {idx + 1}: Converted HTTP to HTTPS: {public_id[:80]}...")
                        else:
                            # It's a public_id - construct full Cloudinary URL
                            try:
                                from .utils import get_cloudinary_url
                                from django.conf import settings
                                
                                full_url = get_cloudinary_url(public_id)
                                if not full_url:
                                    cloud_name = getattr(settings, 'CLOUDINARY_CLOUD_NAME', 'detdm1snc')
                                    full_url = f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}"
                                    print(f"   ⚠️ Image {idx + 1}: SDK returned None, using manual: {full_url[:80]}...")
                                else:
                                    print(f"   ✅ Image {idx + 1}: Constructed via SDK: {full_url[:80]}...")
                                img_data['image_url'] = full_url
                            except Exception as e:
                                print(f"   ⚠️ Image {idx + 1}: SDK failed: {e}, using manual fallback")
                                from django.conf import settings
                                cloud_name = getattr(settings, 'CLOUDINARY_CLOUD_NAME', 'detdm1snc')
                                full_url = f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}"
                                img_data['image_url'] = full_url
                                print(f"   ✅ Image {idx + 1}: Used manual fallback: {full_url[:80]}...")
                    else:
                        print(f"   ⚠️ Image {idx + 1}: No image field, cannot construct URL")
                else:
                    print(f"   ✅ Image {idx + 1}: Already has valid HTTPS URL: {current_url[:80]}...")
        
        # CRITICAL: Ensure primary_image has valid HTTPS image_url
        if representation.get('primary_image'):
            primary = representation['primary_image']
            primary_url = primary.get('image_url', '')
            primary_image_field = primary.get('image')
            
            print(f"   primary_image: image_url='{primary_url[:80] if primary_url else 'None'}...', image_field='{primary_image_field[:50] if primary_image_field else 'None'}...'")
            
            if not primary_url or not primary_url.startswith('https://'):
                if primary_image_field:
                    public_id = str(primary_image_field).strip()
                    
                    if public_id.startswith('http://') or public_id.startswith('https://'):
                        if public_id.startswith('http://'):
                            public_id = public_id.replace('http://', 'https://', 1)
                        primary['image_url'] = public_id
                        print(f"   ✅ primary_image: Converted HTTP to HTTPS: {public_id[:80]}...")
                    else:
                        try:
                            from .utils import get_cloudinary_url
                            from django.conf import settings
                            
                            full_url = get_cloudinary_url(public_id)
                            if not full_url:
                                cloud_name = getattr(settings, 'CLOUDINARY_CLOUD_NAME', 'detdm1snc')
                                full_url = f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}"
                            primary['image_url'] = full_url
                            print(f"   ✅ primary_image: Constructed URL: {full_url[:80]}...")
                        except Exception as e:
                            from django.conf import settings
                            cloud_name = getattr(settings, 'CLOUDINARY_CLOUD_NAME', 'detdm1snc')
                            full_url = f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}"
                            primary['image_url'] = full_url
                            print(f"   ✅ primary_image: Used manual fallback: {full_url[:80]}...")
        
        # FINAL VERIFICATION: Log what we're returning
        final_images = representation.get('images', [])
        final_primary = representation.get('primary_image')
        print(f"✅ PropertyDetailSerializer.to_representation: FINAL CHECK for Property ID={instance.id}")
        print(f"   Images count: {len(final_images)}")
        for idx, img in enumerate(final_images[:3], 1):
            img_url = img.get('image_url', 'None')
            print(f"   Image {idx} image_url: '{img_url[:80] if img_url and img_url != 'None' else 'None'}...'")
        if final_primary:
            primary_url = final_primary.get('image_url', 'None')
            print(f"   Primary image_url: '{primary_url[:80] if primary_url and primary_url != 'None' else 'None'}...'")
        else:
            print(f"   Primary image: None")
        
        # ADMIN-ONLY: Remove contact_name and contact_phone for non-admin users
        request = self.context.get('request')
        is_admin = False
        if request and request.user and request.user.is_authenticated:
            is_admin = (
                request.user.is_staff or 
                request.user.is_superuser or 
                request.user.email in [
                    'admin@ereft.com', 
                    'melaku.garsamo@gmail.com', 
                    'cb.garsamo@gmail.com', 
                    'lydiageleta45@gmail.com'
                ]
            )
        
        if not is_admin:
            representation.pop('contact_name', None)
            representation.pop('contact_phone', None)
            print(f"   🔒 Removed contact info for non-admin user: {request.user.username if request and request.user else 'anonymous'}")
        else:
            print(f"   ✅ Admin user: contact_name={representation.get('contact_name', 'None')}, contact_phone={representation.get('contact_phone', 'None')}")
        
        return representation
    
    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(user=request.user).exists()
        return False
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return None
    
    def get_review_count(self, obj):
        return obj.reviews.count()

class PropertySearchSerializer(serializers.Serializer):
    """Serializer for property search filters"""
    query = serializers.CharField(required=False)
    property_type = serializers.ChoiceField(choices=Property.PROPERTY_TYPES, required=False)
    listing_type = serializers.ChoiceField(choices=Property.LISTING_TYPES, required=False)
    min_price = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    max_price = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    min_bedrooms = serializers.IntegerField(min_value=0, required=False)
    max_bedrooms = serializers.IntegerField(min_value=0, required=False)
    min_bathrooms = serializers.DecimalField(max_digits=3, decimal_places=1, required=False)
    max_bathrooms = serializers.DecimalField(max_digits=3, decimal_places=1, required=False)
    min_square_feet = serializers.IntegerField(min_value=0, required=False)
    max_square_feet = serializers.IntegerField(min_value=0, required=False)
    city = serializers.CharField(required=False)
    state = serializers.CharField(required=False)
    has_garage = serializers.BooleanField(required=False)
    has_pool = serializers.BooleanField(required=False)
    has_garden = serializers.BooleanField(required=False)
    is_furnished = serializers.BooleanField(required=False)
    sort_by = serializers.ChoiceField(
        choices=['price', '-price', 'created_at', '-created_at', 'bedrooms', '-bedrooms'],
        required=False
    )
    page = serializers.IntegerField(min_value=1, required=False, default=1)
    page_size = serializers.IntegerField(min_value=1, max_value=100, required=False, default=20)
