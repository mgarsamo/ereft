#!/usr/bin/env python
"""
Script to verify PostgreSQL is configured correctly
Run this on Render to ensure database persistence
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection
from django.conf import settings
from listings.models import Property, User

def main():
    print("=" * 60)
    print("PostgreSQL Configuration Verification")
    print("=" * 60)
    
    # Check environment variables
    print("\n📋 Environment Variables:")
    db_url = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRE_DATABASE_URL')
    if db_url:
        print(f"   DATABASE_URL: {'✅ Set' if os.environ.get('DATABASE_URL') else '❌ Not set'}")
        print(f"   POSTGRE_DATABASE_URL: {'✅ Set' if os.environ.get('POSTGRE_DATABASE_URL') else '❌ Not set'}")
        print(f"   Database URL (first 50 chars): {db_url[:50]}...")
    else:
        print("   ❌ Neither DATABASE_URL nor POSTGRE_DATABASE_URL is set!")
        print("   ⚠️  This means SQLite will be used and data will NOT persist!")
        return False
    
    # Check Django database configuration
    print("\n🔧 Django Database Configuration:")
    db_engine = settings.DATABASES['default']['ENGINE']
    db_name = settings.DATABASES['default'].get('NAME', 'unknown')
    db_host = settings.DATABASES['default'].get('HOST', 'unknown')
    db_port = settings.DATABASES['default'].get('PORT', 'unknown')
    
    print(f"   Engine: {db_engine}")
    print(f"   Name: {db_name}")
    print(f"   Host: {db_host}")
    print(f"   Port: {db_port}")
    
    # Verify PostgreSQL
    if 'postgresql' in db_engine or 'postgres' in db_engine:
        print("\n✅ PostgreSQL is configured correctly!")
    else:
        print(f"\n❌ ERROR: Database engine is NOT PostgreSQL!")
        print(f"   Current engine: {db_engine}")
        print(f"   Data will NOT persist across deployments!")
        return False
    
    # Test connection
    print("\n🔌 Testing Database Connection:")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            print(f"   ✅ Connection successful!")
            print(f"   PostgreSQL version: {version[:80]}...")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False
    
    # Check existing data
    print("\n📊 Database Contents:")
    try:
        prop_count = Property.objects.count()
        user_count = User.objects.count()
        user_created_props = Property.objects.exclude(owner__username='melaku_agent').count()
        
        print(f"   Total Properties: {prop_count}")
        print(f"   User-Created Properties: {user_created_props}")
        print(f"   Sample Properties: {prop_count - user_created_props}")
        print(f"   Total Users: {user_count}")
        
        if prop_count > 0:
            print("\n✅ Data exists in database - persistence is working!")
        else:
            print("\nℹ️  Database is empty (normal for first deployment)")
    except Exception as e:
        print(f"   ❌ Error querying database: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All checks passed! PostgreSQL is configured correctly.")
    print("✅ User-created properties will persist across deployments.")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

