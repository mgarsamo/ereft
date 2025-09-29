# FILE: ereft_api/settings.py

from pathlib import Path
import os

# Import production dependencies conditionally
try:
    import dj_database_url
    from decouple import config
    HAS_PROD_DEPS = True
except ImportError:
    HAS_PROD_DEPS = False
    # Fallback config function for local development
    def config(key, default=None, cast=None):
        value = os.environ.get(key, default)
        if cast and value is not None:
            if cast == bool:
                # Handle case where default is already a boolean
                if isinstance(value, bool):
                    return value
                if isinstance(value, str):
                    return value.lower() in ('true', '1', 'yes', 'on')
                return bool(value)
            elif callable(cast):
                return cast(value)
        return value

# ------------------------------------------------------
# Base directory (used throughout for paths)
# ------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

# ------------------------------------------------------
# SECURITY KEY (required for cryptographic signing)
# ------------------------------------------------------
SECRET_KEY = config('SECRET_KEY', default='django-insecure-3$9z&u@k%v!x=8k6_nzr8#z-g8*_d@7%lm7nb4^=7&eqjvjk4p')

# ------------------------------------------------------
# Debug and allowed hosts for development
# ------------------------------------------------------
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,192.168.12.129,*.onrender.com,ereft-api.onrender.com', cast=lambda v: [s.strip() for s in v.split(',')])

# ------------------------------------------------------
# Installed Applications
# ------------------------------------------------------
INSTALLED_APPS = [
    # Default Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',           # For building RESTful APIs
    'rest_framework.authtoken', # For token-based auth
    'rest_framework_simplejwt', # For JWT authentication
    'rest_framework_simplejwt.token_blacklist', # For JWT token blacklisting
    'djoser',                   # For enhanced JWT authentication endpoints
    # 'django_filters',           # Removed for deployment
    'corsheaders',              # For CORS support (mobile apps)
    'cloudinary',               # For image uploads and storage

    # Local apps
    'listings',       # Your property listings app
    'payments',       # Payment processing app
]

# ------------------------------------------------------
# Middleware Configuration
# ------------------------------------------------------
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # CORS middleware (must be first)
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Whitenoise for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ------------------------------------------------------
# CORS Configuration (for mobile apps)
# ------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True  # Allow all origins for mobile apps
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000,http://localhost:8081,http://127.0.0.1:8081',
    cast=lambda v: [s.strip() for s in v.split(',')]
)

# Additional CORS headers for mobile apps
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# CSRF settings for API - Disabled for JWT authentication
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=False, cast=bool)  # True in production
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript access for mobile apps
CSRF_COOKIE_SAMESITE = 'Lax'  # Allow cross-site requests for mobile apps
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='https://ereft-api.onrender.com,https://*.onrender.com,https://*.ngrok-free.app',
    cast=lambda v: [s.strip() for s in v.split(',')]
)

# ------------------------------------------------------
# URL and WSGI Configuration
# ------------------------------------------------------
ROOT_URLCONF = 'urls'               # ✅ Flat structure
WSGI_APPLICATION = 'wsgi.application'

# ------------------------------------------------------
# Templates (default)
# ------------------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Add templates directory
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # Required for admin and auth
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ------------------------------------------------------
# Database Configuration
# ------------------------------------------------------
# Use DATABASE_URL from environment (Render) or fallback to SQLite
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Production: Use DATABASE_URL from Render
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
else:
    # Development: Use SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ------------------------------------------------------
# Password validation (default)
# ------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ------------------------------------------------------
# Internationalization (default)
# ------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------
# Static and Media Files
# ------------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Whitenoise for serving static files in production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'   # Served at http://127.0.0.1:8000/media/
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # Where uploads are stored

# ------------------------------------------------------
# REST Framework Configuration
# ------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',  # Keep for backward compatibility
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        # 'django_filters.rest_framework.DjangoFilterBackend',  # Disabled for deployment
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

# ------------------------------------------------------
# JWT Configuration - Production Ready
# ------------------------------------------------------
from datetime import timedelta

# JWT Secret Key (use environment variable for production)
JWT_SECRET_KEY = config('JWT_SECRET_KEY', default=SECRET_KEY)

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),  # 7 days for mobile app
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),  # 30 days
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': JWT_SECRET_KEY,  # Use dedicated JWT secret key
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': 'ereft-api',
    'JWK_URL': None,
    'LEEWAY': 0,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    'JTI_CLAIM': 'jti',
    'TOKEN_OBTAIN_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenObtainPairSerializer',
    'TOKEN_REFRESH_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenRefreshSerializer',
    'TOKEN_VERIFY_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenVerifySerializer',
    'TOKEN_BLACKLIST_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenBlacklistSerializer',
    'SLIDING_TOKEN_OBTAIN_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer',
    'SLIDING_TOKEN_REFRESH_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer',
}

# ------------------------------------------------------
# Djoser Configuration - Enhanced JWT Authentication
# ------------------------------------------------------
DJOSER = {
    'LOGIN_FIELD': 'email',
    'USER_CREATE_PASSWORD_RETYPE': True,
    'USERNAME_CHANGED_EMAIL_CONFIRMATION': True,
    'PASSWORD_CHANGED_EMAIL_CONFIRMATION': True,
    'SEND_CONFIRMATION_EMAIL': True,
    'SET_USERNAME_RETYPE': True,
    'SET_PASSWORD_RETYPE': True,
    'PASSWORD_RESET_CONFIRM_URL': 'password/reset/confirm/{uid}/{token}',
    'USERNAME_RESET_CONFIRM_URL': 'username/reset/confirm/{uid}/{token}',
    'ACTIVATION_URL': 'activate/{uid}/{token}',
    'SEND_ACTIVATION_EMAIL': True,
    'SERIALIZERS': {
        'user_create': 'djoser.serializers.UserCreateSerializer',
        'user': 'djoser.serializers.UserSerializer',
        'current_user': 'djoser.serializers.UserSerializer',
        'user_delete': 'djoser.serializers.UserDeleteSerializer',
    },
    'PERMISSIONS': {
        'user': ['rest_framework.permissions.IsAuthenticated'],
        'user_list': ['rest_framework.permissions.IsAuthenticated'],
    },
    'HIDE_USERS': False,
    'TOKEN_MODEL': None,  # Use JWT tokens instead of Djoser tokens
}

# ------------------------------------------------------
# Email Configuration for Verification
# ------------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@ereft.com')

# ------------------------------------------------------
# Twilio Configuration for SMS Verification
# ------------------------------------------------------
TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID', default='')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN', default='')
TWILIO_PHONE_NUMBER = config('TWILIO_PHONE_NUMBER', default='')

# ------------------------------------------------------
# Security Settings for Production
# ------------------------------------------------------
# Session settings
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=False, cast=bool)  # True in production
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_REDIRECT_EXEMPT = []
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)  # True in production
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ------------------------------------------------------
# Default primary key field type
# ------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ------------------------------------------------------
# Login Redirect Fix for Browsable API
# ------------------------------------------------------
LOGIN_REDIRECT_URL = '/api/profile/'
LOGOUT_REDIRECT_URL = '/api/'

# ------------------------------------------------------
# File Upload Settings
# ------------------------------------------------------
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Email configuration handled above in production section

# ------------------------------------------------------
# Media and File Upload Configuration
# ------------------------------------------------------
# Maximum file upload size (10MB)
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# Allowed image formats
ALLOWED_IMAGE_FORMATS = ['jpg', 'jpeg', 'png', 'gif', 'webp']

# Image processing settings
IMAGE_MAX_SIZE = (1200, 800)  # Maximum dimensions
IMAGE_QUALITY = 85  # JPEG quality

# ------------------------------------------------------
# Payment Configuration (Stripe)
# ------------------------------------------------------
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', '')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')

# ------------------------------------------------------
# Google Maps Configuration
# ------------------------------------------------------
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', 'AIzaSyAWis-jNmUwxCikA2FG7QqLi-nz7jEvadY')

# ------------------------------------------------------
# Google OAuth Configuration
# ------------------------------------------------------
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
GOOGLE_IOS_CLIENT_ID = os.environ.get('GOOGLE_IOS_CLIENT_ID', '')

# ------------------------------------------------------
# Firebase Configuration
# ------------------------------------------------------
FIREBASE_CONFIG = {
    'apiKey': os.environ.get('FIREBASE_API_KEY', ''),
    'authDomain': os.environ.get('FIREBASE_AUTH_DOMAIN', ''),
    'projectId': os.environ.get('FIREBASE_PROJECT_ID', ''),
    'storageBucket': os.environ.get('FIREBASE_STORAGE_BUCKET', ''),
    'messagingSenderId': os.environ.get('FIREBASE_MESSAGING_SENDER_ID', ''),
    'appId': os.environ.get('FIREBASE_APP_ID', ''),
}

# ------------------------------------------------------
# Cloudinary Configuration
# ------------------------------------------------------
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME', 'detdm1snc'),
    api_key=os.environ.get('CLOUDINARY_API_KEY', '935983952526243'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET', 'ZbaIe1eVXx0wdL3XYhDjExCfQb8'),
    secure=True
)

# Cloudinary environment variables
CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME', 'detdm1snc')
CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY', '935983952526243')
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET', 'ZbaIe1eVXx0wdL3XYhDjExCfQb8')
CLOUDINARY_UPLOAD_PRESET = os.environ.get('CLOUDINARY_UPLOAD_PRESET', 'ereft')

# Cloudinary settings
CLOUDINARY = {
    'cloud_name': os.environ.get('CLOUDINARY_CLOUD_NAME', 'detdm1snc'),
    'api_key': os.environ.get('CLOUDINARY_API_KEY', '935983952526243'),
    'api_secret': os.environ.get('CLOUDINARY_API_SECRET', 'ZbaIe1eVXx0wdL3XYhDjExCfQb8'),
    'secure': True,
}
