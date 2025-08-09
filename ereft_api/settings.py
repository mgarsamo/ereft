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
                return value.lower() in ('true', '1', 'yes', 'on')
            elif callable(cast):
                return cast(value)
        return value

# ------------------------------------------------------
# Base directory (used throughout for paths)
# ------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

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
    # 'django_filters',           # For advanced filtering - disabled for deployment
    'corsheaders',              # For CORS support (mobile apps)

    # Local apps
    'listings',                 # Your property listings app
    'payments',                 # Payment processing app
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

# CSRF settings for API
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
# Database (default SQLite for development)
# ------------------------------------------------------
if HAS_PROD_DEPS:
    DATABASES = {
        'default': dj_database_url.config(
            default=f'sqlite:///{BASE_DIR}/db.sqlite3',
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Fallback to simple SQLite for local development
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
        'rest_framework.authentication.TokenAuthentication',
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

# ------------------------------------------------------
# Email Configuration (for development)
# ------------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_USE_TLS = False
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''

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
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')

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
