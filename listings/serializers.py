# FILE: ereft_api/listings/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    UserProfile, Property, PropertyImage, Favorite, PropertyView,
    SearchHistory, Contact, Neighborhood, PropertyReview
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
        """BULLETPROOF: Always return image URL - construct from public_id or use stored URL"""
        if not obj or not obj.image:
            return None
        
        image_value = str(obj.image).strip()
        if not image_value or image_value in ['None', 'null', '']:
            return None
        
        # If it's already a full URL (starts with http/https), return it directly
        if image_value.startswith('http://') or image_value.startswith('https://'):
            # Convert HTTP to HTTPS
            if image_value.startswith('http://'):
                image_value = image_value.replace('http://', 'https://', 1)
            return image_value
        
        # If it's a public_id (like "ereft_properties/nggejftgnzxzwuitw3wp"), construct the URL
        # Public IDs don't start with http, they're just identifiers
        if image_value and not image_value.startswith('http'):
            try:
                from .utils import get_cloudinary_url
                # Construct full Cloudinary URL from public_id
                cloudinary_url = get_cloudinary_url(image_value)
                if cloudinary_url:
                    return cloudinary_url
            except Exception as e:
                print(f"⚠️ PropertyImageSerializer: Failed to construct URL from public_id '{image_value}': {e}")
        
        # Fallback: try to construct URL manually using public_id
        if image_value and '/' in image_value:  # Likely a public_id
            try:
                from django.conf import settings
                cloud_name = getattr(settings, 'CLOUDINARY_CLOUD_NAME', 'detdm1snc')
                # Construct secure URL: https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}.{format}
                # Since we don't know the format, try common ones or just use the public_id
                url = f"https://res.cloudinary.com/{cloud_name}/image/upload/{image_value}"
                return url
            except:
                pass
        
        return None
    
    def to_representation(self, instance):
        """BULLETPROOF: Always construct full URL from public_id stored in image field"""
        representation = super().to_representation(instance)
        
        # CRITICAL: image field contains public_id (e.g., "ereft_properties/nggejftgnzxzwuitw3wp")
        # We need to construct the full Cloudinary URL from it
        image_field = representation.get('image')
        image_url = representation.get('image_url')
        
        # If image_url is already set by get_image_url(), use it
        if image_url and image_url.startswith('https://'):
            representation['image_url'] = image_url
            return representation
        
        # Otherwise, construct from image field (public_id)
        if image_field:
            public_id = str(image_field).strip()
            
            # If it's already a full URL, use it directly
            if public_id.startswith('http://') or public_id.startswith('https://'):
                if public_id.startswith('http://'):
                    public_id = public_id.replace('http://', 'https://', 1)
                representation['image_url'] = public_id
                return representation
            
            # It's a public_id - construct full Cloudinary URL
            # public_id format: "ereft_properties/nggejftgnzxzwuitw3wp"
            try:
                from .utils import get_cloudinary_url
                from django.conf import settings
                
                # Try to use get_cloudinary_url which uses Cloudinary SDK
                full_url = get_cloudinary_url(public_id)
                
                if full_url:
                    representation['image_url'] = full_url
                    print(f"✅ PropertyImageSerializer: Constructed URL from public_id '{public_id}': {full_url[:80]}...")
                    return representation
            except Exception as e:
                print(f"⚠️ PropertyImageSerializer: Failed to use get_cloudinary_url: {e}")
            
            # Fallback: Construct URL manually
            try:
                from django.conf import settings
                cloud_name = getattr(settings, 'CLOUDINARY_CLOUD_NAME', 'detdm1snc')
                # CRITICAL: Construct full Cloudinary URL format:
                # https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}
                # Cloudinary will serve the image with the correct format automatically
                # Public ID format: "ereft_properties/nggejftgnzxzwuitw3wp"
                full_url = f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}"
                representation['image_url'] = full_url
                print(f"✅ PropertyImageSerializer: Constructed URL manually from public_id '{public_id}': {full_url}")
                return representation
            except Exception as e:
                print(f"⚠️ PropertyImageSerializer: Failed to construct URL manually: {e}")
                import traceback
                traceback.print_exc()
        
        # If all else fails, ensure image_url is set (even if None)
        representation['image_url'] = image_url if image_url else None
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
    primary_image = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = [
            'id', 'title', 'price', 'property_type', 'listing_type',
            'address', 'city', 'sub_city', 'kebele', 'bedrooms', 'bathrooms',
            'area_sqm', 'images', 'primary_image', 'is_favorited', 'created_at', 'status'
        ]
    
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
            'has_air_conditioning', 'has_heating', 'images'
        ]
    
    # Note: Property creation is handled by perform_create in views.py
    # to properly handle file uploads and image processing

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
    
    def get_primary_image(self, obj):
        # CRITICAL: Get primary image - must return object with image_url
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            serialized = PropertyImageSerializer(primary_image).data
            # Ensure image_url is set
            if not serialized.get('image_url') and serialized.get('image'):
                serialized['image_url'] = str(serialized['image']).strip()
                if serialized['image_url'].startswith('http://'):
                    serialized['image_url'] = serialized['image_url'].replace('http://', 'https://', 1)
            return serialized
        else:
            # Try to get first image if no primary
            first_image = obj.images.first()
            if first_image:
                serialized = PropertyImageSerializer(first_image).data
                # Ensure image_url is set
                if not serialized.get('image_url') and serialized.get('image'):
                    serialized['image_url'] = str(serialized['image']).strip()
                    if serialized['image_url'].startswith('http://'):
                        serialized['image_url'] = serialized['image_url'].replace('http://', 'https://', 1)
                return serialized
        return None
    
    def to_representation(self, instance):
        """CRITICAL: Ensure images are ALWAYS included with valid image_url"""
        representation = super().to_representation(instance)
        
        # CRITICAL: Query images directly from database to ensure they're included
        db_images = list(instance.images.all().order_by('order', 'created_at')[:4])
        images_data = representation.get('images', [])
        
        # If serializer didn't include images, add them from database
        if not images_data or len(images_data) == 0:
            if db_images:
                representation['images'] = [PropertyImageSerializer(img).data for img in db_images]
                print(f"🔍 PropertyDetailSerializer.to_representation: Added {len(db_images)} images from database")
        
        # CRITICAL: Ensure every image has image_url set to a valid HTTPS URL
        if representation.get('images'):
            for img_data in representation['images']:
                # Get URL from image_url or image field
                image_url = img_data.get('image_url')
                image_field = img_data.get('image')
                
                # If image_url is missing, use image field (which contains the Cloudinary URL)
                if not image_url and image_field:
                    image_url = str(image_field).strip()
                
                if image_url:
                    # Ensure HTTPS
                    if image_url.startswith('http://'):
                        image_url = image_url.replace('http://', 'https://', 1)
                    # Set image_url
                    img_data['image_url'] = image_url
                else:
                    # If still no URL, this image is invalid
                    print(f"⚠️ PropertyDetailSerializer: Image {img_data.get('id')} has no valid URL")
        
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
