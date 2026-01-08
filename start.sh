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

# CRITICAL: Verify database connection and ensure PostgreSQL is being used
# Do this BEFORE populating data to ensure we're using the right database
echo "🔍 Verifying database connection and persistence..."
python manage.py shell -c "
import os
from django.db import connection
from django.conf import settings
from listings.models import Property, User

try:
    # Check which database engine is being used
    db_engine = settings.DATABASES['default']['ENGINE']
    db_name = settings.DATABASES['default'].get('NAME', 'unknown')
    
    print(f'📊 Database Engine: {db_engine}')
    print(f'📊 Database Name: {db_name}')
    
    # Verify it's PostgreSQL
    if 'postgresql' in db_engine or 'postgres' in db_engine:
        print('✅ PostgreSQL database confirmed - data WILL persist across deployments')
    else:
        print('❌ WARNING: NOT using PostgreSQL! Data will NOT persist!')
        print(f'   Current engine: {db_engine}')
        print('   Please set POSTGRE_DATABASE_URL in Render environment variables')
    
    # Test database connection
    with connection.cursor() as cursor:
        cursor.execute('SELECT version()')
        version = cursor.fetchone()[0]
        print(f'✅ Database connection: OK')
        print(f'   Version: {version[:50]}...')
    
    # Count existing data
    prop_count = Property.objects.count()
    user_count = User.objects.count()
    user_created_props = Property.objects.exclude(owner__username='melaku_agent').count()
    
    print(f'📊 Total properties in database: {prop_count}')
    print(f'📊 User-created properties: {user_created_props}')
    print(f'📊 Sample properties: {prop_count - user_created_props}')
    print(f'📊 Total users in database: {user_count}')
    
    if prop_count > 0:
        print('✅ Data persistence verified - properties exist in database!')
    else:
        print('ℹ️ Database is empty - this is normal for first deployment')
        
except Exception as e:
    print(f'❌ Database verification error: {e}')
    import traceback
    traceback.print_exc()
" 2>&1 || echo "⚠️ Could not verify database connection"

# Populate sample data (only if database is empty or has very few properties)
# IMPORTANT: This only adds sample data, NEVER deletes user-created properties
# This runs AFTER database verification to ensure we're using PostgreSQL
echo ""
echo "🏠 Checking if sample data population is needed..."
PROPERTY_COUNT=$(python manage.py shell -c "from listings.models import Property; print(Property.objects.count())" 2>/dev/null || echo "0")

echo "📊 Current property count: $PROPERTY_COUNT"

# Always try to populate if count is less than 25 (should have ~24 sample properties)
# This ensures sample data is populated even if some properties exist
if [ "$PROPERTY_COUNT" -lt "25" ]; then
    echo "📝 Database has $PROPERTY_COUNT properties. Populating sample data..."
    echo "⚠️ NOTE: This will only ADD sample data, never delete existing properties."
    echo "🔄 Running: python manage.py populate_sample_data"
    
    # Run populate_sample_data with explicit error handling
    python manage.py populate_sample_data 2>&1
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 0 ]; then
        echo "✅ Sample data population completed successfully"
        # Verify properties were created
        sleep 2  # Give database a moment to commit
        NEW_COUNT=$(python manage.py shell -c "from listings.models import Property; print(Property.objects.count())" 2>/dev/null || echo "0")
        echo "📊 New property count: $NEW_COUNT"
        
        if [ "$NEW_COUNT" -eq "$PROPERTY_COUNT" ]; then
            echo "⚠️ WARNING: Property count did not increase. Sample data may not have been created."
            echo "⚠️ This could indicate a database connection issue."
        else
            echo "✅ Properties successfully created! ($PROPERTY_COUNT → $NEW_COUNT)"
        fi
    else
        echo "❌ Sample data population failed with exit code: $EXIT_CODE"
        echo "⚠️ Attempting to continue anyway, but sample data may not be available."
        echo "⚠️ Check the logs above for error details."
    fi
else
    echo "✅ Database already has $PROPERTY_COUNT properties. Skipping sample data population."
    echo "✅ User-created properties are preserved and will not be affected."
fi

# Test welcome email (only on first start or if explicitly needed)
# Commented out by default to avoid sending test emails on every restart
# Uncomment the line below if you want to test email on every start
# python manage.py test_welcome_email

# Start Gunicorn
echo "🚀 Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:$PORT wsgi:application
