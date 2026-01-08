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

# Populate sample data AUTOMATICALLY on every deployment
# IMPORTANT: This only adds sample data, NEVER deletes user-created properties
# This runs AFTER database verification to ensure we're using PostgreSQL
echo ""
echo "🏠 AUTOMATIC SAMPLE DATA POPULATION"
echo "============================================================"
echo "🔄 Running populate_sample_data automatically on deployment..."
echo "⚠️ NOTE: This will only ADD sample data, never delete existing properties."
echo ""

# Run populate_sample_data with explicit error handling and full output
echo "📝 Executing: python manage.py populate_sample_data"
python manage.py populate_sample_data
EXIT_CODE=$?

echo ""
echo "============================================================"

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Sample data population command completed successfully"
    
    # Verify properties were created
    sleep 3  # Give database a moment to commit all transactions
    echo "🔍 Verifying properties were created..."
    
    FINAL_COUNT=$(python manage.py shell -c "from listings.models import Property; print(Property.objects.count())" 2>/dev/null || echo "0")
    SAMPLE_COUNT=$(python manage.py shell -c "from listings.models import Property, User; agent = User.objects.filter(username='melaku_agent').first(); print(Property.objects.filter(owner=agent).count() if agent else 0)" 2>/dev/null || echo "0")
    
    echo "📊 Final property count: $FINAL_COUNT"
    echo "📊 Sample properties: $SAMPLE_COUNT"
    
    if [ "$SAMPLE_COUNT" -lt "20" ]; then
        echo "⚠️ WARNING: Only $SAMPLE_COUNT sample properties found. Expected ~24."
        echo "⚠️ This might indicate an issue. Check logs above for details."
    else
        echo "✅ Sample data population successful! $SAMPLE_COUNT sample properties available."
    fi
else
    echo "❌ Sample data population failed with exit code: $EXIT_CODE"
    echo "⚠️ Check the logs above for error details."
    echo "⚠️ The application will continue, but sample data may not be available."
fi

echo "============================================================"
echo ""

# Test welcome email (only on first start or if explicitly needed)
# Commented out by default to avoid sending test emails on every restart
# Uncomment the line below if you want to test email on every start
# python manage.py test_welcome_email

# Start Gunicorn
echo "🚀 Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:$PORT wsgi:application
