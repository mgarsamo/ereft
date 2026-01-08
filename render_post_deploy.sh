#!/bin/bash
# Post-deploy script for Render
# This script runs after each deployment to populate sample data and test welcome email

set -e  # Exit on error

echo "🚀 Starting post-deploy tasks..."

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run migrations (if not already run)
echo "📊 Running database migrations..."
python manage.py migrate --noinput

# Populate sample data (only if database is empty or has very few properties)
echo "🏠 Checking if sample data population is needed..."
PROPERTY_COUNT=$(python manage.py shell -c "from listings.models import Property; print(Property.objects.count())" 2>/dev/null || echo "0")

if [ "$PROPERTY_COUNT" -lt "5" ]; then
    echo "📝 Database has $PROPERTY_COUNT properties. Populating sample data..."
    python manage.py populate_sample_data
else
    echo "✅ Database already has $PROPERTY_COUNT properties. Skipping sample data population."
fi

# Test welcome email
echo "📧 Testing welcome email functionality..."
python manage.py test_welcome_email

echo "✅ Post-deploy tasks completed successfully!"

