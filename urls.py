# FILE: Ereft/ereft_api/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.contrib.auth.views import LoginView, LogoutView
from rest_framework.authtoken.views import obtain_auth_token

# ------------------------------------------------------
# Root API Landing View
# ------------------------------------------------------
def home_view(request):
    return JsonResponse({
        "message": "Welcome to Ereft Real Estate API!",
        "version": "1.0.0",
        "endpoints": {
            "admin": "/admin/",
            "api": "/api/",
            "auth": {
                "login": "/api/auth/login/",
                "logout": "/api/auth/logout/",
                "token": "/api/auth/token/",
                "register": "/api/auth/register/",  # new
            },
            "properties": "/api/properties/",
            "search": "/api/properties/search/",
            "favorites": "/api/favorites/",
            "profile": "/api/profile/",
        },
        "documentation": "Use /api/ for detailed endpoint information"
    })

# ------------------------------------------------------
# Health Check View for Railway
# ------------------------------------------------------
def health_check(request):
    """Health check endpoint for Railway deployment"""
    return JsonResponse({
        "status": "healthy",
        "service": "Ereft API",
        "timestamp": "2025-01-27T00:00:00Z"
    }, status=200)

# ------------------------------------------------------
# URL Patterns
# ------------------------------------------------------
urlpatterns = [
    path('', home_view, name='api_root'),                      # API root index
    path('health/', health_check, name='health_check'),        # Health check for Railway
    path('admin/', admin.site.urls),                           # Django admin
    path('api/', include('listings.urls')),                    # Property listings API
    path('api/payments/', include('payments.urls')),           # Payment API
    path('api-auth/', include('rest_framework.urls')),         # Browsable API login/logout

    # Authentication endpoints
    path('api/auth/token/', obtain_auth_token, name='api_token_auth'),
    path('api/auth/login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),
]

# ------------------------------------------------------
# Serve media files in development
# ------------------------------------------------------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
