"""
Admin Dashboard API Views for Ereft Platform
Provides full visibility into users, listings, and platform activity
"""
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Property, UserProfile
from datetime import timedelta

def is_admin_user(user):
    """Check if user is admin (superuser, staff, or melaku.garsamo@gmail.com)"""
    if not user.is_authenticated:
        return False
    # Simple admin check: superuser, staff, or specific admin email
    if user.is_superuser or user.is_staff:
        return True
    if hasattr(user, 'email') and user.email == 'melaku.garsamo@gmail.com':
        return True
    return False

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard_stats(request):
    """
    Get comprehensive platform statistics for admin dashboard
    """
    if not is_admin_user(request.user):
        return Response(
            {'detail': 'Admin access required.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Calculate stats
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    total_properties = Property.objects.count()
    active_properties = Property.objects.filter(is_active=True, is_published=True).count()
    
    # Recent activity (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    new_users = User.objects.filter(date_joined__gte=thirty_days_ago).count()
    new_properties = Property.objects.filter(created_at__gte=thirty_days_ago).count()
    
    # Properties by type
    properties_by_type = Property.objects.values('property_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Properties by listing type
    properties_by_listing = Property.objects.values('listing_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Users with most listings
    top_listers = User.objects.annotate(
        listing_count=Count('owned_properties')
    ).filter(listing_count__gt=0).order_by('-listing_count')[:10]
    
    # Recent users (last 50)
    recent_users = User.objects.order_by('-date_joined')[:50].values(
        'id', 'username', 'email', 'first_name', 'last_name', 
        'date_joined', 'is_active', 'is_staff'
    )
    
    # Recent properties (last 50)
    recent_properties = Property.objects.select_related('owner').order_by('-created_at')[:50].values(
        'id', 'title', 'property_type', 'listing_type', 'price', 'city',
        'owner__id', 'owner__username', 'owner__email',
        'created_at', 'is_active', 'is_published'
    )
    
    return Response({
        'overview': {
            'total_users': total_users,
            'active_users': active_users,
            'total_properties': total_properties,
            'active_properties': active_properties,
            'new_users_30d': new_users,
            'new_properties_30d': new_properties,
        },
        'properties_by_type': list(properties_by_type),
        'properties_by_listing': list(properties_by_listing),
        'top_listers': [
            {
                'user_id': u.id,
                'username': u.username,
                'email': u.email,
                'listing_count': u.listing_count
            }
            for u in top_listers
        ],
        'recent_users': list(recent_users),
        'recent_properties': list(recent_properties),
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_all_users(request):
    """
    Get all users with detailed information
    """
    if not is_admin_user(request.user):
        return Response(
            {'detail': 'Admin access required.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    users = User.objects.annotate(
        listing_count=Count('owned_properties'),
        favorite_count=Count('favorites')
    ).order_by('-date_joined')
    
    users_data = []
    for user in users:
        try:
            profile = user.profile
        except:
            profile = None
        
        users_data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined,
            'last_login': user.last_login,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'listing_count': user.listing_count,
            'favorite_count': user.favorite_count,
            'profile': {
                'phone_number': profile.phone_number if profile else None,
                'is_agent': profile.is_agent if profile else False,
                'company_name': profile.company_name if profile else None,
            } if profile else None,
        })
    
    return Response({
        'count': len(users_data),
        'results': users_data
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_all_properties(request):
    """
    Get all properties with owner linkage
    """
    if not is_admin_user(request.user):
        return Response(
            {'detail': 'Admin access required.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    properties = Property.objects.select_related('owner', 'agent').prefetch_related('images').order_by('-created_at')
    
    properties_data = []
    for prop in properties:
        properties_data.append({
            'id': str(prop.id),
            'title': prop.title,
            'property_type': prop.property_type,
            'listing_type': prop.listing_type,
            'price': float(prop.price),
            'city': prop.city,
            'sub_city': prop.sub_city,
            'address': prop.address,
            'bedrooms': prop.bedrooms,
            'bathrooms': float(prop.bathrooms) if prop.bathrooms else None,
            'area_sqm': prop.area_sqm,
            'status': prop.status,
            'is_active': prop.is_active,
            'is_published': prop.is_published,
            'is_featured': prop.is_featured,
            'views_count': prop.views_count,
            'created_at': prop.created_at.isoformat() if prop.created_at else None,
            'updated_at': prop.updated_at.isoformat() if prop.updated_at else None,
            'owner': {
                'id': prop.owner.id,
                'username': prop.owner.username,
                'email': prop.owner.email,
                'first_name': prop.owner.first_name,
                'last_name': prop.owner.last_name,
            } if prop.owner else None,
            'agent': {
                'id': prop.agent.id,
                'username': prop.agent.username,
                'email': prop.agent.email,
            } if prop.agent else None,
            'image_count': prop.images.count(),
        })
    
    return Response({
        'count': len(properties_data),
        'results': properties_data
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_user_listings(request, user_id):
    """
    Get all listings for a specific user
    """
    if not is_admin_user(request.user):
        return Response(
            {'detail': 'Admin access required.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response(
            {'detail': 'User not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    properties = Property.objects.filter(owner=user).order_by('-created_at')
    
    properties_data = []
    for prop in properties:
        properties_data.append({
            'id': str(prop.id),
            'title': prop.title,
            'property_type': prop.property_type,
            'listing_type': prop.listing_type,
            'price': float(prop.price),
            'city': prop.city,
            'status': prop.status,
            'is_active': prop.is_active,
            'is_published': prop.is_published,
            'created_at': prop.created_at.isoformat() if prop.created_at else None,
        })
    
    return Response({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        },
        'listing_count': len(properties_data),
        'listings': properties_data
    })

