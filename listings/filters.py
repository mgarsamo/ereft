import django_filters
from django_filters import rest_framework as filters
from .models import Property
from django.db import models

class PropertyFilter(filters.FilterSet):
    """
    Advanced filtering for properties
    """
    # Price range filtering
    min_price = filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')
    
    # Location filtering
    city = filters.CharFilter(lookup_expr='icontains')
    state = filters.CharFilter(lookup_expr='icontains')
    zip_code = filters.CharFilter(lookup_expr='icontains')
    
    # Property details filtering
    min_bedrooms = filters.NumberFilter(field_name="bedrooms", lookup_expr='gte')
    max_bedrooms = filters.NumberFilter(field_name="bedrooms", lookup_expr='lte')
    min_bathrooms = filters.NumberFilter(field_name="bathrooms", lookup_expr='gte')
    max_bathrooms = filters.NumberFilter(field_name="bathrooms", lookup_expr='lte')
    
    # Square footage filtering
    min_sqft = filters.NumberFilter(field_name="square_feet", lookup_expr='gte')
    max_sqft = filters.NumberFilter(field_name="square_feet", lookup_expr='lte')
    
    # Year built filtering
    min_year = filters.NumberFilter(field_name="year_built", lookup_expr='gte')
    max_year = filters.NumberFilter(field_name="year_built", lookup_expr='lte')
    
    # Features filtering
    has_garage = filters.BooleanFilter()
    has_pool = filters.BooleanFilter()
    has_garden = filters.BooleanFilter()
    has_balcony = filters.BooleanFilter()
    is_furnished = filters.BooleanFilter()
    has_air_conditioning = filters.BooleanFilter()
    has_heating = filters.BooleanFilter()
    
    # Status filtering
    is_featured = filters.BooleanFilter()
    is_active = filters.BooleanFilter()
    
    # Search by title/description
    search = filters.CharFilter(method='search_filter')
    
    class Meta:
        model = Property
        fields = {
            'property_type': ['exact'],
            'listing_type': ['exact'],
            'country': ['exact'],
        }
    
    def search_filter(self, queryset, name, value):
        """
        Search in title and description
        """
        return queryset.filter(
            models.Q(title__icontains=value) |
            models.Q(description__icontains=value) |
            models.Q(address__icontains=value) |
            models.Q(city__icontains=value)
        )

class LocationFilter(filters.FilterSet):
    """
    Location-based filtering
    """
    latitude = filters.NumberFilter()
    longitude = filters.NumberFilter()
    radius = filters.NumberFilter(method='filter_by_radius')
    
    class Meta:
        model = Property
        fields = ['city', 'state', 'zip_code']
    
    def filter_by_radius(self, queryset, name, value):
        """
        Filter properties within a certain radius (in km)
        """
        from django.contrib.gis.geos import Point
        from django.contrib.gis.db.models.functions import Distance
        
        lat = self.data.get('latitude')
        lng = self.data.get('longitude')
        radius = value
        
        if lat and lng and radius:
            point = Point(float(lng), float(lat), srid=4326)
            return queryset.filter(
                location__distance_lte=(point, radius * 1000)  # Convert km to meters
            ).annotate(
                distance=Distance('location', point)
            ).order_by('distance')
        
        return queryset
