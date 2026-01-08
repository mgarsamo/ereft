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
        """BULLETPROOF: Always return image URL from image field"""
        if not obj or not obj.image:
            return None
        
        url = str(obj.image).strip()
        if not url or url in ['None', 'null', '']:
            return None
        
        # Convert HTTP to HTTPS
        if url.startswith('http://'):
            url = url.replace('http://', 'https://', 1)
        
        # Return if valid HTTPS URL
        if url.startswith('https://'):
            return url
        
        # If not a URL, try to generate from public_id (shouldn't happen)
        if url:
            try:
                from .utils import get_cloudinary_url
                return get_cloudinary_url(url)
            except:
                pass
        
        return None
    
    def to_representation(self, instance):
        """BULLETPROOF: image_url ALWAYS equals image field (the Cloudinary URL)"""
        representation = super().to_representation(instance)
        
        # CRITICAL: image_url MUST be set from image field
        image_field = representation.get('image')
        
        if image_field:
            url = str(image_field).strip()
            # Convert HTTP to HTTPS
            if url.startswith('http://'):
                url = url.replace('http://', 'https://', 1)
            # Set image_url to image field value
            representation['image_url'] = url
        else:
            # If no image field, ensure image_url is None
            representation['image_url'] = None
        
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

class PropertyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating properties - Ethiopia fields, m² units"""
    images = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    
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
