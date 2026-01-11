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
    google_id = models.CharField(max_length=100, blank=True, null=True, unique=True)  # Google OAuth ID
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
        ('vacation_home', 'Vacation Home'),
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
    description = models.TextField(blank=True, null=True)
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
    bedrooms = models.PositiveIntegerField(blank=True, null=True)
    bathrooms = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
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
    
    # Listing Contact Information (Optional - nullable, safe for existing data)
    contact_name = models.CharField(max_length=255, blank=True, null=True)
    contact_phone = models.CharField(max_length=50, blank=True, null=True)
    
    # Vacation Home Specific Fields (only for vacation_home property type)
    availability_start_date = models.DateField(blank=True, null=True, help_text='Earliest date property can be booked')
    availability_end_date = models.DateField(blank=True, null=True, help_text='Latest date property is available (optional)')
    min_stay_nights = models.PositiveIntegerField(default=1, help_text='Minimum number of nights per booking')
    max_stay_nights = models.PositiveIntegerField(blank=True, null=True, help_text='Maximum number of nights per booking (optional)')
    booking_preference = models.CharField(
        max_length=20,
        choices=[
            ('instant', 'Instant Booking'),
            ('request', 'Request to Book (Requires Approval)'),
        ],
        default='request',
        help_text='Booking preference for vacation homes'
    )
    # Guest Configuration (Vacation Homes Only)
    max_adults = models.PositiveIntegerField(default=2, help_text='Maximum number of adults allowed')
    max_children = models.PositiveIntegerField(default=0, help_text='Maximum number of children allowed (ages 0-17)')
    pets_allowed = models.BooleanField(default=False, help_text='Whether pets are allowed on the property')
    
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
    
    def save(self, *args, **kwargs):
        """Override save to add logging and validation"""
        if self.pk:
            print(f"📝 Property UPDATE: {self.title} (ID: {self.pk})")
        else:
            print(f"✨ Property CREATE: {self.title}")
        super().save(*args, **kwargs)
        print(f"✅ Property saved: {self.title} (ID: {self.pk})")
    
    def get_full_address(self):
        """Get formatted full address"""
        parts = [self.address]
        if self.sub_city:
            parts.append(self.sub_city)
        parts.append(self.city)
        if self.kebele:
            parts.append(f"Kebele {self.kebele}")
        parts.append(self.country)
        return ", ".join(parts)
    
    def get_owner_info(self):
        """Get formatted owner information"""
        return {
            'username': self.owner.username,
            'email': self.owner.email,
            'name': f"{self.owner.first_name or ''} {self.owner.last_name or ''}".strip() or self.owner.username
        }
    
    def update_views(self):
        """Increment view count"""
        self.views_count += 1
        self.save(update_fields=['views_count'])

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

class Availability(models.Model):
    """
    Daily availability status for vacation homes
    """
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('booked', 'Booked / Reserved'),
        ('blocked', 'Blocked / Unavailable'),
    ]
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='availability_dates')
    date = models.DateField(help_text='Specific date for availability status')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    notes = models.TextField(blank=True, null=True, help_text='Optional notes (e.g., maintenance, personal use)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['property', 'date']
        ordering = ['date']
        indexes = [
            models.Index(fields=['property', 'date']),
            models.Index(fields=['date', 'status']),
        ]
        verbose_name_plural = "Availabilities"
    
    def __str__(self):
        return f"{self.property.title} - {self.date} ({self.status})"

class Booking(models.Model):
    """
    Booking requests and confirmed bookings for vacation homes
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='bookings')
    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    guest_name = models.CharField(max_length=255, help_text='Guest name (if not logged in)')
    guest_email = models.EmailField()
    guest_phone = models.CharField(max_length=50)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    nights = models.PositiveIntegerField(help_text='Number of nights')
    total_price = models.DecimalField(max_digits=12, decimal_places=2, help_text='Total booking price')
    message = models.TextField(blank=True, null=True, help_text='Guest inquiry message')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_instant_booking = models.BooleanField(default=False, help_text='Whether this was an instant booking')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['property', 'check_in_date', 'check_out_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Booking for {self.property.title} - {self.check_in_date} to {self.check_out_date} ({self.status})"
    
    def save(self, *args, **kwargs):
        """Override save to automatically create availability entries for booked dates"""
        is_new = self.pk is None
        old_status = None
        if not is_new:
            try:
                old_instance = Booking.objects.get(pk=self.pk)
                old_status = old_instance.status
            except Booking.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # If booking is confirmed (newly created or status changed to confirmed), mark dates as booked
        if self.status == 'confirmed' and (is_new or old_status != 'confirmed'):
            from datetime import timedelta
            current_date = self.check_in_date
            while current_date < self.check_out_date:
                Availability.objects.update_or_create(
                    property=self.property,
                    date=current_date,
                    defaults={
                        'status': 'booked',
                        'notes': f'Booked by {self.guest_name}'
                    }
                )
                current_date += timedelta(days=1)
        
        # If booking is cancelled or status changed from confirmed, mark dates as available
        if self.status == 'cancelled' and old_status == 'confirmed':
            from datetime import timedelta
            current_date = self.check_in_date
            while current_date < self.check_out_date:
                # Remove booked status (set to available or delete if no longer needed)
                Availability.objects.filter(
                    property=self.property,
                    date=current_date,
                    status='booked'
                ).delete()
                current_date += timedelta(days=1)

class RecurringAvailabilityRule(models.Model):
    """
    Recurring availability rules for vacation homes (e.g., "Available every weekend")
    """
    RULE_TYPES = [
        ('weekly', 'Weekly Pattern'),
        ('monthly', 'Monthly Pattern'),
        ('yearly', 'Yearly Pattern (Holidays)'),
    ]
    
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='recurring_rules')
    rule_type = models.CharField(max_length=20, choices=RULE_TYPES)
    status = models.CharField(max_length=20, choices=Availability.STATUS_CHOICES, default='available')
    
    # Weekly pattern fields
    days_of_week = models.JSONField(default=list, blank=True, help_text='List of day numbers (0=Monday, 6=Sunday) for weekly patterns')
    
    # Monthly pattern fields
    day_of_month = models.PositiveIntegerField(blank=True, null=True, help_text='Day of month (1-31) for monthly patterns')
    
    # Yearly pattern fields (holidays)
    month = models.PositiveIntegerField(blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(12)], help_text='Month (1-12) for yearly patterns')
    day = models.PositiveIntegerField(blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(31)], help_text='Day of month for yearly patterns')
    
    # Date range for rule application
    start_date = models.DateField(help_text='Rule applies from this date')
    end_date = models.DateField(blank=True, null=True, help_text='Rule applies until this date (optional)')
    
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Recurring rule for {self.property.title} - {self.rule_type} ({self.status})"
