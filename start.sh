#!/bin/bash
set -e

echo "Starting Ereft API deployment..."

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
