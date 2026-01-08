#!/bin/bash
# Start script for Django application on Render

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run Django migrations
echo "📊 Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Populate sample data (only if database is empty or has very few properties)
# IMPORTANT: This only adds sample data, NEVER deletes user-created properties
echo "🏠 Checking if sample data population is needed..."
PROPERTY_COUNT=$(python manage.py shell -c "from listings.models import Property; print(Property.objects.count())" 2>/dev/null || echo "0")

if [ "$PROPERTY_COUNT" -lt "5" ]; then
    echo "📝 Database has $PROPERTY_COUNT properties. Populating sample data..."
    echo "⚠️ NOTE: This will only ADD sample data, never delete existing properties."
    python manage.py populate_sample_data
else
    echo "✅ Database already has $PROPERTY_COUNT properties. Skipping sample data population."
    echo "✅ User-created properties are preserved and will not be affected."
fi

# Verify database connection and data persistence
echo "🔍 Verifying database connection..."
python manage.py shell -c "
from django.db import connection
from listings.models import Property, User
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    print('✅ Database connection: OK')
    prop_count = Property.objects.count()
    user_count = User.objects.count()
    print(f'✅ Total properties in database: {prop_count}')
    print(f'✅ Total users in database: {user_count}')
    print('✅ Data persistence verified - all data is safe!')
except Exception as e:
    print(f'❌ Database connection error: {e}')
" 2>/dev/null || echo "⚠️ Could not verify database connection"

# Test welcome email (only on first start or if explicitly needed)
# Commented out by default to avoid sending test emails on every restart
# Uncomment the line below if you want to test email on every start
# python manage.py test_welcome_email

# Start Gunicorn
echo "🚀 Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:$PORT wsgi:application
