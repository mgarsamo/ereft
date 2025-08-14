# FILE: ereft_api/listings/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    UserProfile, Property, PropertyImage, Favorite, PropertyView,
    SearchHistory, Contact, Neighborhood, PropertyReview
)

class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']

class UserProfileSerializer(serializers.ModelSerializer):
    """User profile serializer"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'

class PropertyImageSerializer(serializers.ModelSerializer):
    """Property image serializer"""
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'image_url', 'caption', 'is_primary', 'order', 'created_at']
    
    def get_image_url(self, obj):
        """Get the image URL - either from Cloudinary or direct URL"""
        if obj.image:
            # If it's already a URL, return it
            if obj.image.startswith('http'):
                return obj.image
            # If it's a Cloudinary public_id, generate URL
            else:
                from .utils import get_cloudinary_url
                return get_cloudinary_url(obj.image)
        return None

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
    primary_image = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = [
            'id', 'title', 'price', 'property_type', 'listing_type',
            'address', 'city', 'sub_city', 'kebele', 'bedrooms', 'bathrooms',
            'area_sqm', 'primary_image', 'is_favorited', 'created_at', 'status'
        ]
    
    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return primary_image.image  # image is a CharField storing Cloudinary URL
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
    
    def create(self, validated_data):
        try:
            images_data = validated_data.pop('images', [])
            property_obj = Property.objects.create(**validated_data)
            
            # Create PropertyImage objects for uploaded images
            if images_data:
                for i, image_url in enumerate(images_data):
                    if image_url:  # Only create if URL is not empty
                        try:
                            PropertyImage.objects.create(
                                property=property_obj,
                                image=image_url,  # Store Cloudinary URL directly
                                is_primary=(i == 0),  # First image is primary
                                order=i
                            )
                        except Exception as img_error:
                            print(f"🔧 PropertyCreateSerializer: Error creating PropertyImage: {img_error}")
                            # Continue with other images even if one fails
                            continue
            
            return property_obj
        except Exception as e:
            print(f"🔧 PropertyCreateSerializer: Error in create method: {e}")
            raise serializers.ValidationError(f"Failed to create property: {str(e)}")

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
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return PropertyImageSerializer(primary_image).data
        return None
    
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
