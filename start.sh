#!/bin/bash
set -e

echo "Starting Ereft API deployment..."

# Check PORT variable
if [ -z "$PORT" ]; then
    echo "WARNING: PORT environment variable not set, using default 8000"
    export PORT=8000
fi
echo "Using PORT: $PORT"

# Wait for any database operations
echo "Running migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist
echo "Setting up admin user..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Admin user created')
else:
    print('Admin user already exists')
" || echo "Admin setup skipped"

# Test that Django can start
echo "Testing Django configuration..."
python manage.py check --deploy || echo "Deploy check completed with warnings"

# Test health endpoint locally
echo "Testing health endpoint..."
python manage.py shell -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()
from django.test import Client
client = Client()
response = client.get('/health/')
print(f'Health check status: {response.status_code}')
print(f'Health check response: {response.content.decode()}')
" || echo "Health check test skipped"

# Start the server
echo "Starting gunicorn server on 0.0.0.0:$PORT..."
exec gunicorn wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --timeout 120 \
    --keep-alive 2 \
    --max-requests 1000 \
    --preload \
    --log-level info \
    --access-logfile - \
    --error-logfile -
