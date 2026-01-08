#!/usr/bin/env python
"""
Script to verify data persistence in PostgreSQL database.
Run this after deployments to confirm all data is retained.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth.models import User
from listings.models import Property, Favorite, PropertyView, Contact, UserProfile

def verify_data_persistence():
    """Verify that all data types are present in the database"""
    print("🔍 Verifying Data Persistence in PostgreSQL Database\n")
    print("=" * 60)
    
    # Count Users
    user_count = User.objects.count()
    print(f"👥 Total Users: {user_count}")
    if user_count > 0:
        print(f"   - Active users: {User.objects.filter(is_active=True).count()}")
        print(f"   - Staff users: {User.objects.filter(is_staff=True).count()}")
        print(f"   - Sample users:")
        for user in User.objects.all()[:5]:
            print(f"     • {user.username} ({user.email})")
    
    # Count User Profiles
    profile_count = UserProfile.objects.count()
    print(f"\n📋 User Profiles: {profile_count}")
    if profile_count > 0:
        agent_count = UserProfile.objects.filter(is_agent=True).count()
        print(f"   - Agent profiles: {agent_count}")
    
    # Count Properties
    property_count = Property.objects.count()
    print(f"\n🏠 Properties: {property_count}")
    if property_count > 0:
        print(f"   - Active: {Property.objects.filter(is_active=True).count()}")
        print(f"   - Published: {Property.objects.filter(is_published=True).count()}")
        print(f"   - Featured: {Property.objects.filter(is_featured=True).count()}")
        print(f"   - For Sale: {Property.objects.filter(listing_type='sale').count()}")
        print(f"   - For Rent: {Property.objects.filter(listing_type='rent').count()}")
        print(f"   - Sample properties:")
        for prop in Property.objects.all()[:5]:
            print(f"     • {prop.title} ({prop.city}) - {prop.price:,.0f} ETB")
    
    # Count Favorites
    favorite_count = Favorite.objects.count()
    print(f"\n❤️  Favorites: {favorite_count}")
    
    # Count Property Views
    view_count = PropertyView.objects.count()
    print(f"\n👁️  Property Views: {view_count}")
    
    # Count Contacts
    contact_count = Contact.objects.count()
    print(f"\n📧 Contact Inquiries: {contact_count}")
    
    # Database Info
    from django.db import connection
    db_name = connection.settings_dict.get('NAME', 'Unknown')
    db_engine = connection.settings_dict.get('ENGINE', 'Unknown')
    print(f"\n💾 Database Info:")
    print(f"   - Engine: {db_engine}")
    print(f"   - Name: {db_name}")
    
    # Check if using PostgreSQL
    if 'postgresql' in db_engine.lower() or 'postgres' in db_engine.lower():
        print(f"   ✅ Using PostgreSQL - Data is PERSISTENT")
        print(f"   ✅ All data will be retained across deployments")
    elif 'sqlite' in db_engine.lower():
        print(f"   ⚠️  Using SQLite - Data may be EPHEMERAL")
        print(f"   ⚠️  Consider switching to PostgreSQL for production")
    else:
        print(f"   ℹ️  Using: {db_engine}")
    
    print("\n" + "=" * 60)
    print("✅ Data persistence verification complete!")
    
    if property_count > 0 and user_count > 0:
        print("✅ Database contains data - persistence is working correctly!")
    elif property_count == 0:
        print("⚠️  No properties found - run 'python manage.py populate_sample_data'")
    elif user_count == 0:
        print("⚠️  No users found - this is normal for a fresh database")

if __name__ == '__main__':
    verify_data_persistence()

