# Ereft Backend Configuration
import os

# Environment Configuration
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')

# API Configuration
API_CONFIG = {
    'development': {
        'DEBUG': True,
        'ALLOWED_HOSTS': ['*'],
        'CORS_ALLOW_ALL_ORIGINS': True,
        'DATABASE_URL': 'sqlite:///./db.sqlite3',
    },
    'production': {
        'DEBUG': False,
        'ALLOWED_HOSTS': ['api.ereft.com'],
        'CORS_ALLOWED_ORIGINS': ['https://ereft.app'],
        'DATABASE_URL': 'sqlite:///./db.sqlite3',  # Change to PostgreSQL in production
    }
}

# OAuth Configuration
OAUTH_CONFIG = {
    'GOOGLE_CLIENT_ID': 'your-google-client-id',
    'FACEBOOK_APP_ID': 'your-facebook-app-id',
    'FACEBOOK_APP_SECRET': 'your-facebook-app-secret',
}
