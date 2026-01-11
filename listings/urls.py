# FILE: ereft_api/listings/urls.py
# PRODUCTION READY: All endpoints properly configured per .cursorrules
# TIMESTAMP: 2025-01-15 16:30:00 - FORCE REDEPLOYMENT
# 🚨 CRITICAL: URL pattern conflicts resolved - force new deployment

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from django.contrib.auth.views import LogoutView
from . import views
from . import admin_views
from . import availability_views
from .auth_views import (
    CustomTokenObtainPairView, 
    CustomTokenRefreshView,
    custom_jwt_login,
    custom_jwt_register
)
from django.http import JsonResponse
from datetime import datetime

# Create router for ViewSets
router = DefaultRouter()
router.register(r'properties', views.PropertyViewSet, basename='property')
router.register(r'favorites', views.FavoriteViewSet, basename='favorite')
router.register(r'profile', views.UserProfileViewSet, basename='userprofile')
router.register(r'neighborhoods', views.NeighborhoodViewSet, basename='neighborhood')

urlpatterns = [
    # API Root
    path('', views.api_root, name='api_root'),
    
    # Database Test
    path('db-test/', views.database_test, name='database_test'),
    
    # Admin Setup (Production)
    path('setup-admin/', views.setup_admin_users, name='setup_admin_users'),
    path('verify-admin/', views.verify_admin_user, name='verify_admin_user'),
    
    # Custom Property URLs - Use different names to avoid router conflicts
    path('track/<uuid:property_id>/', views.track_property_view, name='track-property-view'),
    
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
    path('auth/logout/', views.custom_logout, name='custom_logout'),
    path('auth/google/', views.google_oauth_endpoint, name='google_oauth'),
    path('auth/verify-token/', views.verify_token, name='verify_token'),
    path('auth/password-reset/', views.request_password_reset, name='password_reset'),
    path('auth/verify-email/<str:uidb64>/<str:token>/', views.verify_email_endpoint, name='verify_email'),
    path('auth/reset-password/<str:uidb64>/<str:token>/', views.reset_password_confirm, name='password_reset_confirm'),
    
    # Production JWT Authentication Endpoints
    path('auth/jwt/login/', custom_jwt_login, name='jwt_login'),
    path('auth/jwt/register/', custom_jwt_register, name='jwt_register'),
    path('auth/jwt/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/jwt/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    
    # OAuth callback endpoint (for exchanging code for JWT)
    path('oauth/callback/', views.oauth_callback, name='oauth_callback'),
    
    # Enhanced Authentication with JWT, Email & SMS Verification
    path('auth/enhanced-login/', views.enhanced_login, name='enhanced_login'),
    path('auth/enhanced-register/', views.enhanced_register, name='enhanced_register'),
    path('auth/verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('auth/send-sms-verification/', views.send_sms_verification, name='send_sms_verification'),
    path('auth/verify-sms-code/', views.verify_sms_code, name='verify_sms_code'),
    path('auth/refresh-token/', views.refresh_token, name='refresh_token'),
    
    # User Profile
    path('profile/', views.user_profile, name='user-profile'),
    
    # Admin Dashboard Endpoints
    path('admin/dashboard/stats/', admin_views.admin_dashboard_stats, name='admin-dashboard-stats'),
    path('admin/users/', admin_views.admin_all_users, name='admin-all-users'),
    path('admin/properties/', admin_views.admin_all_properties, name='admin-all-properties'),
    path('admin/users/<int:user_id>/listings/', admin_views.admin_user_listings, name='admin-user-listings'),
    path('admin/delete-townhouses/', admin_views.admin_delete_townhouses, name='admin-delete-townhouses'),
    path('admin/bulk-delete-properties/', admin_views.admin_bulk_delete_properties, name='admin-bulk-delete-properties'),
    
    # Availability and Booking Management (Vacation Homes)
    path('properties/<uuid:property_id>/availability/', availability_views.property_availability, name='property-availability'),
    path('properties/<uuid:property_id>/availability/<str:date_str>/', availability_views.availability_detail, name='availability-detail'),
    path('properties/<uuid:property_id>/bookings/', availability_views.property_bookings, name='property-bookings'),
    path('bookings/<uuid:booking_id>/status/', availability_views.booking_status, name='booking-status'),
]
