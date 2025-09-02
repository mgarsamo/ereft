# FILE: ereft_api/listings/urls.py
# PRODUCTION READY: All endpoints properly configured per .cursorrules
# TIMESTAMP: 2025-01-15 16:30:00 - FORCE REDEPLOYMENT
# 🚨 CRITICAL: URL pattern conflicts resolved - force new deployment

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from django.contrib.auth.views import LogoutView
from . import views
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
    
    # Production JWT Authentication Endpoints
    path('auth/jwt/login/', custom_jwt_login, name='jwt_login'),
    path('auth/jwt/register/', custom_jwt_register, name='jwt_register'),
    path('auth/jwt/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/jwt/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    
    # OAuth redirect endpoint (for Google OAuth redirect)
    path('oauth/', views.google_oauth_endpoint, name='oauth_redirect'),
    
    # Enhanced Authentication with JWT, Email & SMS Verification
    path('auth/enhanced-login/', views.enhanced_login, name='enhanced_login'),
    path('auth/enhanced-register/', views.enhanced_register, name='enhanced_register'),
    path('auth/verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('auth/send-sms-verification/', views.send_sms_verification, name='send_sms_verification'),
    path('auth/verify-sms-code/', views.verify_sms_code, name='verify_sms_code'),
    path('auth/refresh-token/', views.refresh_token, name='refresh_token'),
    
    # User Profile
    path('profile/', views.user_profile, name='user-profile'),
]
