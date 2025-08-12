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
    This endpoint receives the authorization code and redirects with the code
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
        
        # Instead of just redirecting, we need to process the OAuth flow
        # Exchange the authorization code for user tokens and create/login the user
        print(f"🔐 Processing OAuth flow for user signup/login...")
        
        try:
            # Exchange authorization code for access token
            GOOGLE_CLIENT_ID = '91486871350-79fvub6490473eofjpu1jjlhncuiua44.apps.googleusercontent.com'
            GOOGLE_CLIENT_SECRET = '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'
            
            print(f"🔐 Starting OAuth flow with Google...")
            print(f"🔐 Authorization code: {code[:20]}...")
            
            token_url = 'https://oauth2.googleapis.com/token'
            token_data = {
                'client_id': GOOGLE_CLIENT_ID,
                'client_secret': GOOGLE_CLIENT_SECRET,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': 'https://ereft.onrender.com/oauth'
            }
            
            print(f"🔐 Exchanging authorization code for access token...")
            try:
                token_response = requests.post(token_url, data=token_data, timeout=30)
                token_response.raise_for_status()
                token_info = token_response.json()
                print(f"🔐 Token response received: {token_info.keys()}")
            except requests.exceptions.RequestException as req_error:
                print(f"🔐 Google token request failed: {str(req_error)}")
                raise Exception(f'Failed to exchange authorization code: {str(req_error)}')
            
            access_token = token_info.get('access_token')
            if not access_token:
                print(f"🔐 No access token in response: {token_info}")
                raise Exception('Failed to obtain access token from Google')
            
            print(f"🔐 Access token obtained: {access_token[:20]}...")
            
            # Get user info from Google
            user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
            headers = {'Authorization': f'Bearer {access_token}'}
            
            print(f"🔐 Fetching user info from Google...")
            try:
                user_response = requests.get(user_info_url, headers=headers, timeout=30)
                user_response.raise_for_status()
                user_info = user_response.json()
                print(f"🔐 User info received: {user_info.keys()}")
            except requests.exceptions.RequestException as req_error:
                print(f"🔐 Google user info request failed: {str(req_error)}")
                raise Exception(f'Failed to get user info from Google: {str(req_error)}')
            
            # Extract user information
            google_id = user_info.get('id')
            email = user_info.get('email')
            first_name = user_info.get('given_name', '')
            last_name = user_info.get('family_name', '')
            profile_picture = user_info.get('picture')
            
            print(f"🔐 Extracted user info - Email: {email}, Name: {first_name} {last_name}")
            
            if not email:
                print(f"🔐 No email in user info: {user_info}")
                raise Exception('Email is required from Google OAuth')
            
            print(f"🔐 User info received: {email}")
            
            # Check if user already exists
            try:
                # Try to find user by email (Django User model email field is not unique by default)
                # We'll use username instead, or create a unique username from email
                username_from_email = f"google_{email.split('@')[0]}"
                
                try:
                    # First try to find by email
                    user = User.objects.get(email=email)
                    print(f"🔐 Existing user found by email: {email}")
                except User.DoesNotExist:
                    # If not found by email, try by username
                    try:
                        user = User.objects.get(username=username_from_email)
                        print(f"🔐 Existing user found by username: {username_from_email}")
                    except User.DoesNotExist:
                        # User doesn't exist, create new one
                        raise User.DoesNotExist
                
                # Update existing user info
                user.first_name = first_name
                user.last_name = last_name
                user.email = email  # Ensure email is set
                user.save()
                print(f"🔐 Existing user updated: {email}")
                
            except User.DoesNotExist:
                # Create new user (this is the signup part!)
                # Generate a unique username
                base_username = f"google_{email.split('@')[0]}"
                username = base_username
                counter = 1
                
                # Ensure username is unique
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}_{counter}"
                    counter += 1
                
                try:
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        password=None  # No password for OAuth users
                    )
                    print(f"🔐 New user created (signup): {email} with username: {username}")
                except Exception as user_creation_error:
                    print(f"🔐 User creation failed: {str(user_creation_error)}")
                    raise Exception(f'Failed to create user account: {str(user_creation_error)}')
            
            # Generate or get existing token
            try:
                token, created = Token.objects.get_or_create(user=user)
                print(f"🔐 Authentication token generated: {token.key[:10]}...")
            except Exception as token_error:
                print(f"🔐 Token generation error: {str(token_error)}")
                # If Token model fails, create a simple session-based approach
                # For now, we'll use a simple hash as a fallback token
                import hashlib
                fallback_token = hashlib.md5(f"{user.id}_{email}_{datetime.datetime.now().isoformat()}".encode()).hexdigest()
                print(f"🔐 Using fallback token: {fallback_token[:10]}...")
                token = type('Token', (), {'key': fallback_token})()
            
            print(f"🔐 OAuth flow completed successfully for user: {user.username}")
            
            # Now redirect to mobile app with the authentication token
            # This allows the user to be automatically signed in
            mobile_deep_link = f"ereft://oauth?token={token.key}&user_id={user.id}&email={email}&first_name={first_name}&last_name={last_name}&google_id={google_id}"
            
            print(f"🔐 Redirecting to mobile app with authentication data")
            print(f"🔐 Deep link: {mobile_deep_link}")
            
            # Instead of trying to redirect to custom protocol (which Django blocks),
            # we'll return an HTML page with JavaScript that opens the deep link
            # The mobile app can intercept this and handle the authentication
            html_response = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Signing you in...</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                    .spinner {{ border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 20px auto; }}
                    @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
                    .auth-data {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: left; max-width: 500px; margin-left: auto; margin-right: auto; }}
                    .auth-data h3 {{ margin-top: 0; color: #495057; }}
                    .auth-data p {{ margin: 5px 0; font-family: monospace; }}
                </style>
            </head>
            <body>
                <h2>Signing you into Ereft...</h2>
                <div class="spinner"></div>
                <p>Please wait while we complete your sign-in...</p>
                
                <script>
                    // Try to open the mobile app deep link
                    const deepLink = 'ereft://oauth?token={token.key}&user_id={user.id}&email={email}&first_name={first_name}&last_name={last_name}&google_id={google_id}';
                    
                    console.log('Opening deep link:', deepLink);
                    
                    // Multiple attempts to open the deep link
                    let attempts = 0;
                    const maxAttempts = 3;
                    
                    function attemptDeepLink() {{
                        attempts++;
                        console.log('Deep link attempt', attempts, 'of', maxAttempts);
                        
                        try {{
                            // Method 1: Direct location change
                            window.location.href = deepLink;
                            
                            // Method 2: Try using window.open as fallback
                            setTimeout(() => {{
                                if (attempts < maxAttempts) {{
                                    console.log('Trying window.open method...');
                                    window.open(deepLink, '_self');
                                }}
                            }}, 1000);
                            
                        }} catch (error) {{
                            console.error('Deep link attempt failed:', error);
                        }}
                    }}
                    
                    // Start attempting to open the deep link
                    attemptDeepLink();
                    
                    // Retry if needed
                    setTimeout(() => {{
                        if (attempts < maxAttempts) {{
                            attemptDeepLink();
                        }}
                    }}, 2000);
                    
                    // Fallback: if deep link doesn't work, show manual instructions
                    setTimeout(function() {{
                        document.body.innerHTML = `
                            <h2>Sign-in Complete!</h2>
                            <p>You have been successfully signed into Ereft.</p>
                            <p>If you're not automatically redirected to the app, please:</p>
                            <ol style="text-align: left; max-width: 400px; margin: 0 auto;">
                                <li>Return to the Ereft mobile app</li>
                                <li>You should now be signed in automatically</li>
                            </ol>
                            
                            <div class="auth-data">
                                <h3>Authentication Data (for debugging):</h3>
                                <p><strong>Authentication Token:</strong> {token.key[:20]}...</p>
                                <p><strong>User ID:</strong> {user.id}</p>
                                <p><strong>Email:</strong> {email}</p>
                                <p><strong>First Name:</strong> {first_name}</p>
                                <p><strong>Last Name:</strong> {last_name}</p>
                                <p><strong>Google ID:</strong> {google_id}</p>
                            </div>
                            
                            <div style="margin: 30px 0;">
                                <button onclick="window.location.href='ereft://oauth?token={token.key}&user_id={user.id}&email={email}&first_name={first_name}&last_name={last_name}&google_id={google_id}'" 
                                        style="background: #4285F4; color: white; border: none; padding: 15px 30px; border-radius: 8px; font-size: 16px; cursor: pointer; margin: 10px;">
                                    🔗 Open Ereft App
                                </button>
                                <br>
                                <button onclick="window.location.href='ereft://oauth?token={token.key}&user_id={user.id}&email={email}&first_name={first_name}&last_name={last_name}&google_id={google_id}'" 
                                        style="background: #34A853; color: white; border: none; padding: 15px 30px; border-radius: 8px; font-size: 16px; cursor: pointer; margin: 10px;">
                                    📱 Try Deep Link Again
                                </button>
                            </div>
                            
                            <p><em>Note: If you're still not signed in, please try the Google Sign-In button again.</em></p>
                        `;
                    }}, 5000);
                </script>
            </body>
            </html>
            """
            
            print(f"🔐 Returning HTML response with deep link: ereft://oauth?token=...&user_id={user.id}&email={email}")
            
            # Return HTML response instead of redirect
            from django.http import HttpResponse
            return HttpResponse(html_response, content_type='text/html')
            
        except Exception as e:
            print(f"🔐 OAuth processing error: {str(e)}")
            # Return HTML error page instead of redirect
            error_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Sign-in Error</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; color: #721c24; background-color: #f8d7da; }}
                    .error-box {{ background-color: #f5c6cb; border: 1px solid #f5c6cb; border-radius: 5px; padding: 20px; max-width: 500px; margin: 0 auto; }}
                </style>
            </head>
            <body>
                <div class="error-box">
                    <h2>Sign-in Error</h2>
                    <p>We encountered an error while processing your Google sign-in:</p>
                    <p><strong>{str(e)}</strong></p>
                    <p>Please try again or contact support if the problem persists.</p>
                    <p><a href="javascript:history.back()">Go Back</a></p>
                </div>
            </body>
            </html>
            """
            return HttpResponse(error_html, content_type='text/html')
        
    except Exception as e:
        print(f"🔐 OAuth handler error: {str(e)}")
        return JsonResponse({
            'error': f'Unexpected error: {str(e)}'
        }, status=500)

# ------------------------------------------------------
# OAuth Success Handler
# ------------------------------------------------------
@csrf_exempt
def oauth_success_handler(request):
    """
    Handle OAuth success redirect with authorization code
    This endpoint returns the authorization code in a way the mobile app can process
    """
    try:
        print(f"🔐 OAuth success handler called with method: {request.method}")
        print(f"🔐 Request path: {request.path}")
        print(f"🔐 Request GET params: {request.GET}")
        
        # Get the authorization code and state from the redirect
        code = request.GET.get('code')
        state = request.GET.get('state')
        
        print(f"🔐 Success Code: {code}")
        print(f"🔐 Success State: {state}")
        
        if not code:
            return JsonResponse({
                'error': 'No authorization code received'
            }, status=400)
        
        # Return the authorization code and state
        # The mobile app will extract this from the URL
        return JsonResponse({
            'success': True,
            'code': code,
            'state': state,
            'message': 'Authorization code received successfully'
        })
        
    except Exception as e:
        print(f"🔐 OAuth success handler error: {str(e)}")
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
            'redirect_uri': redirect_uri or 'https://ereft.onrender.com/oauth'
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
# Google ID Token Verification View (for mobile app)
# ------------------------------------------------------
@csrf_exempt
@require_http_methods(["POST"])
def google_id_token_verify_view(request):
    try:
        data = json.loads(request.body)
        id_token = data.get('id_token')
        
        if not id_token:
            return JsonResponse({
                'error': 'ID token is required'
            }, status=400)
        
        print(f"🔐 Google ID token verification request received")
        print(f"🔐 ID token length: {len(id_token)}")
        
        # Verify the ID token with Google
        verify_url = 'https://oauth2.googleapis.com/tokeninfo'
        params = {'id_token': id_token}
        
        verify_response = requests.get(verify_url, params=params)
        verify_response.raise_for_status()
        token_info = verify_response.json()
        
        print(f"🔐 Google token verification successful")
        print(f"🔐 Token info: {token_info}")
        
        # Extract user information from verified token
        google_id = token_info.get('sub')
        email = token_info.get('email')
        first_name = token_info.get('given_name', '')
        last_name = token_info.get('family_name', '')
        profile_picture = token_info.get('picture')
        
        if not email:
            return JsonResponse({'error': 'Email is required from Google ID token'}, status=400)
        
        # Create or update user
        try:
            user = User.objects.get(email=email)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            print(f"🔐 Existing user updated: {email}")
        except User.DoesNotExist:
            username = f"google_{google_id}" if google_id else f"google_{email.split('@')[0]}"
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=None
            )
            print(f"🔐 New user created: {email}")
        
        # Generate or get existing token
        token, created = Token.objects.get_or_create(user=user)
        
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
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except requests.RequestException as e:
        return JsonResponse({'error': f'Google token verification failed: {str(e)}'}, status=500)
    except Exception as e:
        return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)

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
    path('oauth/success', oauth_success_handler, name='oauth_success'), # OAuth success handler
    path('api/', include('listings.urls')),                    # Property listings API
    path('api/payments/', include('payments.urls')),           # Payment API
    path('api-auth/', include('rest_framework.urls')),         # Browsable API login/logout

    # Authentication endpoints
    path('api/auth/token/', obtain_auth_token, name='api_token_auth'),
    path('api/auth/login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),
    path('api/auth/google/', google_oauth_view, name='google_oauth'),
    path('api/auth/google/verify/', google_id_token_verify_view, name='google_id_token_verify'),
]

# ------------------------------------------------------
# Serve media files in development
# ------------------------------------------------------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
