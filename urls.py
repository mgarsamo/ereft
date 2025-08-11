# FILE: Ereft/ereft_api/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.contrib.auth.views import LoginView, LogoutView
from rest_framework.authtoken.views import obtain_auth_token
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import requests
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
import datetime

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
# Test endpoint to verify deployment
# ------------------------------------------------------
def test_endpoint(request):
    return JsonResponse({
        'message': 'Backend is working! DEPLOYMENT FORCED!',
        'timestamp': str(datetime.datetime.now()),
        'oauth_routes': ['/oauth', '/oauth/'],
        'deployment_status': 'FORCED_REDEPLOYMENT_COMPLETED'
    })

# ------------------------------------------------------
# OAuth Redirect Handler
# ------------------------------------------------------
@csrf_exempt
def oauth_redirect_handler(request):
    """
    Handle OAuth redirect from Google
    This endpoint receives the authorization code and redirects back to the mobile app
    """
    try:
        print(f"🔐 OAuth redirect handler called with method: {request.method}")
        print(f"🔐 Request path: {request.path}")
        print(f"🔐 Request GET params: {request.GET}")
        
        # Get the authorization code and state from Google's redirect
        code = request.GET.get('code')
        state = request.GET.get('state')
        error = request.GET.get('error')
        
        print(f"🔐 Code: {code}")
        print(f"🔐 State: {state}")
        print(f"🔐 Error: {error}")
        
        if error:
            return JsonResponse({
                'error': f'OAuth error: {error}'
            }, status=400)
        
        if not code:
            return JsonResponse({
                'error': 'No authorization code received'
            }, status=400)
        
        # Return the authorization code and state to the mobile app
        # This will be used by the mobile app to complete the OAuth flow
        return JsonResponse({
            'success': True,
            'code': code,
            'state': state,
            'message': 'Authorization code received successfully'
        })
        
    except Exception as e:
        print(f"🔐 OAuth handler error: {str(e)}")
        return JsonResponse({
            'error': f'Unexpected error: {str(e)}'
        }, status=500)

# ------------------------------------------------------
# Google OAuth View
# ------------------------------------------------------
@csrf_exempt
@require_http_methods(["POST"])
def google_oauth_view(request):
    try:
        data = json.loads(request.body)
        code = data.get('code')
        redirect_uri = data.get('redirect_uri')
        
        if not code:
            return JsonResponse({
                'error': 'Authorization code is required'
            }, status=400)
        
        # Google OAuth configuration
        GOOGLE_CLIENT_ID = '91486871350-79fvub6490473eofjpu1jjlhncuiua44.apps.googleusercontent.com'
        GOOGLE_CLIENT_SECRET = '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'
        
        # Exchange authorization code for access token
        token_url = 'https://oauth2.googleapis.com/token'
        token_data = {
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri or 'ereft://oauth'
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        token_info = token_response.json()
        
        access_token = token_info.get('access_token')
        if not access_token:
            return JsonResponse({
                'error': 'Failed to obtain access token from Google'
            }, status=400)
        
        # Get user info from Google
        user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        headers = {'Authorization': f'Bearer {access_token}'}
        user_response = requests.get(user_info_url, headers=headers)
        user_response.raise_for_status()
        user_info = user_response.json()
        
        # Extract user information
        google_id = user_info.get('id')
        email = user_info.get('email')
        first_name = user_info.get('given_name', '')
        last_name = user_info.get('family_name', '')
        profile_picture = user_info.get('picture')
        
        if not email:
            return JsonResponse({
                'error': 'Email is required from Google OAuth'
            }, status=400)
        
        # Check if user already exists
        try:
            user = User.objects.get(email=email)
            # Update existing user info
            user.first_name = first_name
            user.last_name = last_name
            user.save()
        except User.DoesNotExist:
            # Create new user
            username = f"google_{google_id}" if google_id else f"google_{email.split('@')[0]}"
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=None  # No password for OAuth users
            )
        
        # Generate or get existing token
        token, created = Token.objects.get_or_create(user=user)
        
        # Return user data and token
        return JsonResponse({
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'profile_picture': profile_picture,
                'provider': 'google',
                'google_id': google_id
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON data'
        }, status=400)
    except requests.RequestException as e:
        return JsonResponse({
            'error': f'Google API request failed: {str(e)}'
        }, status=500)
    except Exception as e:
        return JsonResponse({
            'error': f'Unexpected error: {str(e)}'
        }, status=500)

# ------------------------------------------------------
# URL Patterns
# ------------------------------------------------------
urlpatterns = [
    path('', home_view, name='api_root'),                      # API root index
    path('health/', health_check, name='health_check'),        # Health check for Railway
    path('debug/', lambda request: JsonResponse({'status': 'DEBUG_ENDPOINT_WORKING', 'oauth_routes': ['/oauth', '/oauth/']}), name='debug'),  # Debug endpoint
    path('test/', test_endpoint, name='test'),                 # Test endpoint
    path('admin/', admin.site.urls),                           # Django admin
    path('oauth', oauth_redirect_handler, name='oauth_redirect_no_slash'),  # OAuth redirect handler (no slash)
    path('oauth/', oauth_redirect_handler, name='oauth_redirect'),  # OAuth redirect handler (with slash)
    path('api/', include('listings.urls')),                    # Property listings API
    path('api/payments/', include('payments.urls')),           # Payment API
    path('api-auth/', include('rest_framework.urls')),         # Browsable API login/logout

    # Authentication endpoints
    path('api/auth/token/', obtain_auth_token, name='api_token_auth'),
    path('api/auth/login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),
    path('api/auth/google/', google_oauth_view, name='google_oauth'),
]

# ------------------------------------------------------
# Serve media files in development
# ------------------------------------------------------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
