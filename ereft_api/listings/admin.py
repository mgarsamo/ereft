# FILE: ereft_api/listings/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    UserProfile, Property, PropertyImage, Favorite, PropertyView,
    SearchHistory, Contact, Neighborhood, PropertyReview
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'is_agent', 'company_name', 'created_at']
    list_filter = ['is_agent', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone_number', 'company_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'phone_number', 'profile_picture')
        }),
        ('Agent Information', {
            'fields': ('is_agent', 'agent_license', 'company_name', 'bio')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ['image', 'caption', 'is_primary', 'order']

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'property_type', 'listing_type', 'price', 'city', 
        'bedrooms', 'bathrooms', 'owner', 'is_featured', 'is_active', 'views_count'
    ]
    list_filter = [
        'property_type', 'listing_type', 'is_featured', 'is_active', 
        'has_garage', 'has_pool', 'has_garden', 'created_at'
    ]
    search_fields = ['title', 'description', 'address', 'city', 'state']
    readonly_fields = ['id', 'created_at', 'updated_at', 'views_count']
    list_editable = ['is_featured', 'is_active']
    inlines = [PropertyImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'title', 'description', 'property_type', 'listing_type', 'price')
        }),
        ('Location', {
            'fields': ('address', 'city', 'state', 'zip_code', 'country', 'latitude', 'longitude')
        }),
        ('Property Details', {
            'fields': ('bedrooms', 'bathrooms', 'square_feet', 'lot_size', 'year_built')
        }),
        ('Features', {
            'fields': ('has_garage', 'has_pool', 'has_garden', 'has_balcony', 
                      'is_furnished', 'has_air_conditioning', 'has_heating')
        }),
        ('Status', {
            'fields': ('is_featured', 'is_active', 'views_count')
        }),
        ('Relationships', {
            'fields': ('owner', 'agent')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'listed_date'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('owner', 'agent')

@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ['property', 'image_preview', 'caption', 'is_primary', 'order', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['property__title', 'caption']
    list_editable = ['is_primary', 'order']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Preview'

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'property', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'property__title']
    readonly_fields = ['created_at']

@admin.register(PropertyView)
class PropertyViewAdmin(admin.ModelAdmin):
    list_display = ['property', 'user', 'ip_address', 'viewed_at']
    list_filter = ['viewed_at']
    search_fields = ['property__title', 'user__username', 'ip_address']
    readonly_fields = ['viewed_at']

@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'query', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'query']
    readonly_fields = ['created_at']

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'contact_type', 'property', 'is_read', 'created_at']
    list_filter = ['contact_type', 'is_read', 'created_at']
    search_fields = ['name', 'email', 'message', 'property__title']
    list_editable = ['is_read']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Message', {
            'fields': ('message', 'contact_type')
        }),
        ('Property', {
            'fields': ('property',)
        }),
        ('Status', {
            'fields': ('is_read',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Neighborhood)
class NeighborhoodAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'average_price', 'school_rating', 'walk_score', 'transit_score']
    list_filter = ['city', 'created_at']
    search_fields = ['name', 'city', 'description']
    readonly_fields = ['created_at']

@admin.register(PropertyReview)
class PropertyReviewAdmin(admin.ModelAdmin):
    list_display = ['property', 'user', 'rating', 'is_verified', 'created_at']
    list_filter = ['rating', 'is_verified', 'created_at']
    search_fields = ['property__title', 'user__username', 'comment']
    list_editable = ['is_verified']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Review Information', {
            'fields': ('property', 'user', 'rating', 'comment')
        }),
        ('Status', {
            'fields': ('is_verified',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# Customize admin site
admin.site.site_header = "Ereft Real Estate Administration"
admin.site.site_title = "Ereft Admin"
admin.site.index_title = "Welcome to Ereft Real Estate Admin"
