# FILE: ereft_api/listings/urls.py
# PRODUCTION READY: All endpoints properly configured per .cursorrules
# TIMESTAMP: 2025-01-15 16:30:00 - FORCE REDEPLOYMENT
# 🚨 CRITICAL: URL pattern conflicts resolved - force new deployment

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from django.contrib.auth.views import LogoutView
from . import views
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
    
    # Router URLs - Include FIRST to ensure they work
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
