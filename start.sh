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
echo "🏠 Checking if sample data population is needed..."
PROPERTY_COUNT=$(python manage.py shell -c "from listings.models import Property; print(Property.objects.count())" 2>/dev/null || echo "0")

if [ "$PROPERTY_COUNT" -lt "5" ]; then
    echo "📝 Database has $PROPERTY_COUNT properties. Populating sample data..."
    python manage.py populate_sample_data
else
    echo "✅ Database already has $PROPERTY_COUNT properties. Skipping sample data population."
fi

# Test welcome email (only on first start or if explicitly needed)
# Commented out by default to avoid sending test emails on every restart
# Uncomment the line below if you want to test email on every start
# python manage.py test_welcome_email

# Start Gunicorn
echo "🚀 Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:$PORT wsgi:application
