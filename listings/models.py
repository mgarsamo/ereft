# FILE: ereft_api/listings/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid

class UserProfile(models.Model):
    """
    Extended user profile for real estate users (buyers, sellers, agents)
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.CharField(max_length=500, blank=True, null=True)  # Cloudinary URL
    is_agent = models.BooleanField(default=False)
    agent_license = models.CharField(max_length=100, blank=True, null=True)
    company_name = models.CharField(max_length=200, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    # Email verification fields
    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True, null=True)
    verification_token_created = models.DateTimeField(blank=True, null=True)
    
    # SMS verification fields
    phone_verified = models.BooleanField(default=False)
    sms_verification_code = models.CharField(max_length=6, blank=True, null=True)
    sms_verification_code_created = models.DateTimeField(blank=True, null=True)
    
    # Account security fields
    is_locked = models.BooleanField(default=False)
    lockout_until = models.DateTimeField(blank=True, null=True)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Property(models.Model):
    """
    Comprehensive property model for real estate listings
    """
    # Property Types
    PROPERTY_TYPES = [
        ('house', 'House'),
        ('apartment', 'Apartment'),
        ('condo', 'Condo'),
        ('townhouse', 'Townhouse'),
        ('land', 'Land'),
        ('commercial', 'Commercial'),
        ('other', 'Other'),
    ]

    # Listing Types
    LISTING_TYPES = [
        ('sale', 'For Sale'),
        ('rent', 'For Rent'),
        ('sold', 'Sold'),
        ('pending', 'Pending'),
    ]

    # Status choices
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('pending', 'Pending Review'),
        ('inactive', 'Inactive'),
        ('sold', 'Sold'),
        ('rented', 'Rented'),
    ]

    # Basic Info
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    listing_type = models.CharField(max_length=20, choices=LISTING_TYPES)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    price_per_sqm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text='Price per square meter')
    
    # Ethiopia-specific Location Fields
    address = models.CharField(max_length=255, help_text='Full address')
    city = models.CharField(max_length=100, help_text='City (e.g., Addis Ababa)')
    sub_city = models.CharField(max_length=100, blank=True, null=True, help_text='Sub-city (e.g., Bole, Kirkos)')
    kebele = models.CharField(max_length=100, blank=True, null=True, help_text='Kebele/Ward')
    street_name = models.CharField(max_length=255, blank=True, null=True, help_text='Street name')
    house_number = models.CharField(max_length=50, blank=True, null=True, help_text='House/building number')
    country = models.CharField(max_length=100, default="Ethiopia")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    
    # Property Details (using square meters)
    bedrooms = models.PositiveIntegerField()
    bathrooms = models.DecimalField(max_digits=3, decimal_places=1)
    area_sqm = models.PositiveIntegerField(blank=True, null=True, help_text='Area in square meters')
    lot_size_sqm = models.PositiveIntegerField(blank=True, null=True, help_text='Lot size in square meters')
    year_built = models.PositiveIntegerField(blank=True, null=True)
    
    # Features
    has_garage = models.BooleanField(default=False)
    has_pool = models.BooleanField(default=False)
    has_garden = models.BooleanField(default=False)
    has_balcony = models.BooleanField(default=False)
    is_furnished = models.BooleanField(default=False)
    has_air_conditioning = models.BooleanField(default=False)
    has_heating = models.BooleanField(default=False)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', help_text='Property listing status')
    is_published = models.BooleanField(default=True, help_text='Whether the listing is published and visible')
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    views_count = models.PositiveIntegerField(default=0)
    
    # Relationships
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_properties')
    agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='agent_properties')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    listed_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Properties"

    def __str__(self):
        return f"{self.title} - {self.city}"

class PropertyImage(models.Model):
    """
    Multiple images for each property
    """
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.CharField(max_length=500)  # Cloudinary URL
    caption = models.CharField(max_length=255, blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Image for {self.property.title}"

class Favorite(models.Model):
    """
    User favorites/bookmarks
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'property']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} favorited {self.property.title}"

class PropertyView(models.Model):
    """
    Track property views
    """
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='property_views')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='viewed_properties', null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-viewed_at']

class SearchHistory(models.Model):
    """
    Track user search history
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_history')
    query = models.CharField(max_length=500)
    filters = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Search Histories"

class Contact(models.Model):
    """
    Contact form submissions
    """
    CONTACT_TYPES = [
        ('inquiry', 'Property Inquiry'),
        ('showing', 'Request Showing'),
        ('general', 'General Question'),
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='contacts', null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    message = models.TextField()
    contact_type = models.CharField(max_length=20, choices=CONTACT_TYPES, default='inquiry')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Contact from {self.name} - {self.contact_type}"

class Neighborhood(models.Model):
    """
    Neighborhood information
    """
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    average_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    crime_rate = models.CharField(max_length=50, blank=True, null=True)
    school_rating = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    walk_score = models.PositiveIntegerField(blank=True, null=True)
    transit_score = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['name', 'city']

    def __str__(self):
        return f"{self.name}, {self.city}"

class PropertyReview(models.Model):
    """
    Property reviews and ratings
    """
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='property_reviews')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['property', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user.username} for {self.property.title}"
