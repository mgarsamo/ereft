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

# Populate sample data ONLY if database is empty (SAFETY: Never overwrite existing data)
# This runs AFTER migrations and database verification to ensure we're using PostgreSQL
echo ""
echo "🏠 SAMPLE DATA POPULATION CHECK"
echo "============================================================"

# Check if database has existing data (AFTER migrations have run)
USER_COUNT=$(python manage.py shell -c "
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
import django
django.setup()
from django.contrib.auth.models import User
print(User.objects.count())
" 2>/dev/null | tail -1 || echo "0")

PROP_COUNT=$(python manage.py shell -c "
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
import django
django.setup()
from listings.models import Property
print(Property.objects.count())
" 2>/dev/null | tail -1 || echo "0")

echo "📊 Current database state:"
echo "   - Users: $USER_COUNT"
echo "   - Properties: $PROP_COUNT"

# Check if we should populate sample data
# SAFE: populate_sample_data only ADDS properties, never deletes existing ones
# It uses get_or_create with title, so it won't create duplicates
SAMPLE_PROP_COUNT=$(python manage.py shell -c "
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
import django
django.setup()
from listings.models import Property
from django.contrib.auth.models import User
agent = User.objects.filter(username='melaku_agent').first()
if agent:
    print(Property.objects.filter(owner=agent).count())
else:
    print(0)
" 2>/dev/null | tail -1 || echo "0")

echo "📊 Sample properties currently in database: $SAMPLE_PROP_COUNT"

# Always run populate_sample_data - it's safe (only adds, never deletes)
# It will add the 260 new properties + 24 original ones = 284 total sample properties
if [ "$SAMPLE_PROP_COUNT" -lt "280" ]; then
    echo "✅ Populating sample data (safe - only adds, never deletes)..."
    echo "⚠️ NOTE: This will only ADD sample data, never delete existing properties."
    echo ""
    
    # Run populate_sample_data with explicit error handling and full output
    echo "📝 Executing: python manage.py populate_sample_data"
    python manage.py populate_sample_data 2>&1
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 0 ]; then
        echo "✅ Sample data population completed successfully"
    else
        echo "❌ Sample data population failed with exit code: $EXIT_CODE"
        echo "⚠️ Check the logs above for error details."
    fi
else
    echo "✅ Sample data already populated ($SAMPLE_PROP_COUNT sample properties found)"
    echo "⏭️  Skipping sample data population (already have sufficient sample data)"
fi

echo "============================================================"
echo ""

# Update all properties to have status='active' if they don't have a valid status
echo "🔄 Updating property statuses to 'active'..."
python manage.py update_properties_status 2>&1
STATUS_UPDATE_CODE=$?

if [ $STATUS_UPDATE_CODE -eq 0 ]; then
    echo "✅ Property status update completed successfully"
else
    echo "⚠️ Property status update completed with warnings (exit code: $STATUS_UPDATE_CODE)"
fi

# Ensure all admin emails have admin privileges
echo ""
echo "🔐 Ensuring all admin users have admin privileges..."
python manage.py ensure_all_admins 2>&1
ADMIN_UPDATE_CODE=$?

if [ $ADMIN_UPDATE_CODE -eq 0 ]; then
    echo "✅ Admin privilege check completed successfully"
else
    echo "⚠️ Admin privilege check completed with warnings (exit code: $ADMIN_UPDATE_CODE)"
fi

echo ""

# Test welcome email (only on first start or if explicitly needed)
# Commented out by default to avoid sending test emails on every restart
# Uncomment the line below if you want to test email on every start
# python manage.py test_welcome_email

# Start Gunicorn
echo "🚀 Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:$PORT wsgi:application
