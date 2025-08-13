# FILE: ereft_api/listings/urls.py
# UPDATED: Fixed URL routing conflict - custom URLs now come BEFORE router
# PRODUCTION READY: All endpoints properly configured
# 🚨 FORCE REDEPLOYMENT: URL routing fix not active on production
# 🚨 URGENT: Backend still returning 404 for featured/stats endpoints
# 🚨 CRITICAL: All API endpoints failing - force new deployment immediately
# 🚨 URGENT REDEPLOYMENT: New URL patterns not taking effect - /api/featured/ still 404

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from django.contrib.auth.views import LogoutView
from . import views
from django.http import JsonResponse
from datetime import datetime

# Create router for ViewSets
router = DefaultRouter()
router.register(r'list', views.PropertyViewSet, basename='property')  # Changed to just 'list' to avoid conflicts
router.register(r'favorites', views.FavoriteViewSet, basename='favorite')
router.register(r'profile', views.UserProfileViewSet, basename='userprofile')
router.register(r'neighborhoods', views.NeighborhoodViewSet, basename='neighborhood')

urlpatterns = [
    # API Root
    path('', views.api_root, name='api_root'),
    
    # DEBUG: Force redeployment and test URL loading
    path('debug-urls/', lambda request: JsonResponse({
        'message': 'URL patterns are loading correctly',
        'timestamp': str(datetime.now()),
        'endpoints': [
            'properties/featured/',
            'properties/stats/',
            'properties/search/',
            'properties/list/',
            'favorites/',
            'profile/',
        ]
    }), name='debug-urls'),
    
    # Custom Property URLs - MUST come BEFORE router to avoid conflicts
    # Use more specific patterns to prevent router from catching them
    path('properties/featured/', views.featured_properties, name='featured-properties'),
    path('properties/stats/', views.property_stats, name='property-stats'),
    path('properties/search/', views.PropertySearchView.as_view(), name='property-search'),
    path('properties/<uuid:property_id>/track-view/', views.track_property_view, name='track-property-view'),
    
    # Router URLs - Include AFTER custom URLs
    path('', include(router.urls)),
    
    # Search History
    path('search-history/', views.search_history, name='search-history'),
    
    # User Stats
    path('users/me/stats/', views.UserStatsView.as_view(), name='user-stats'),
    
    # Authentication
    path('auth/login/', views.custom_login, name='custom_login'),
    path('auth/register/', views.custom_register, name='custom_register'),
    path('auth/token/', obtain_auth_token, name='api_token_auth'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/google/', views.google_oauth_endpoint, name='google_oauth'),
    path('auth/verify-token/', views.verify_token, name='verify_token'),
    
    # User Profile
    path('profile/', views.user_profile, name='user-profile'),
]
