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
from .models import Property, UserProfile, PropertyImage, Favorite, PropertyView, Contact, PropertyReview, SearchHistory
from django.core.cache import cache
from django.db import transaction
from datetime import timedelta

def is_admin_user(user):
    """Check if user is admin (superuser, staff, or specific admin emails)"""
    if not user.is_authenticated:
        return False
    
    # Simple admin check: superuser, staff, or specific admin emails
    if user.is_superuser or user.is_staff:
        return True
    
    admin_emails = ['admin@ereft.com', 'melaku.garsamo@gmail.com', 'cb.garsamo@gmail.com', 'lydiageleta45@gmail.com']
    
    # Check email (case-insensitive, strip whitespace)
    if hasattr(user, 'email') and user.email:
        user_email = user.email.strip().lower()
        admin_emails_lower = [email.strip().lower() for email in admin_emails]
        if user_email in admin_emails_lower:
            # Auto-grant admin privileges if email matches but flags aren't set
            if not user.is_staff or not user.is_superuser:
                user.is_staff = True
                user.is_superuser = True
                user.is_active = True
                user.save(update_fields=['is_staff', 'is_superuser', 'is_active'])
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
    
    # Don't cache admin properties view - always fetch fresh data
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
            'contact_name': getattr(prop, 'contact_name', None),
            'contact_phone': getattr(prop, 'contact_phone', None),
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_delete_townhouses(request):
    """
    Permanently delete all townhouse properties from the system
    Admin only endpoint
    """
    if not is_admin_user(request.user):
        return Response(
            {'detail': 'Admin access required.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Find all townhouse properties
    townhouse_properties = Property.objects.filter(property_type='townhouse')
    count = townhouse_properties.count()
    
    if count == 0:
        return Response({
            'success': True,
            'message': 'No townhouse properties found. Nothing to delete.',
            'deleted_count': 0
        })
    
    deleted_count = 0
    deleted_ids = []
    
    try:
        with transaction.atomic():
            for prop in townhouse_properties:
                prop_id = prop.id
                prop_title = prop.title
                
                # Delete related PropertyImage objects
                PropertyImage.objects.filter(property=prop).delete()
                
                # Delete related Favorite objects
                Favorite.objects.filter(property=prop).delete()
                
                # Delete the property itself
                prop.delete()
                
                deleted_count += 1
                deleted_ids.append(str(prop_id))
            
            # Clear cache to ensure deleted properties don't appear
            cache.clear()
            
            return Response({
                'success': True,
                'message': f'Successfully deleted {deleted_count} townhouse propert{"y" if deleted_count == 1 else "ies"}.',
                'deleted_count': deleted_count,
                'deleted_ids': deleted_ids[:50],  # Return first 50 IDs
                'total_found': count
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error during deletion: {str(e)}',
            'deleted_count': deleted_count
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_bulk_delete_properties(request):
    """
    Permanently delete multiple properties by their IDs
    Admin only endpoint
    """
    if not is_admin_user(request.user):
        return Response(
            {'detail': 'Admin access required.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    property_ids = request.data.get('property_ids', [])
    
    if not property_ids or not isinstance(property_ids, list) or len(property_ids) == 0:
        return Response(
            {'success': False, 'message': 'property_ids array is required and must not be empty'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    deleted_count = 0
    deleted_ids = []
    not_found_ids = []
    
    try:
        print(f"[BULK DELETE] Starting deletion of {len(property_ids)} properties")
        print(f"[BULK DELETE] Property IDs (first 10): {property_ids[:10]}")
        print(f"[BULK DELETE] Property ID types (first 5): {[type(pid).__name__ for pid in property_ids[:5]]}")
        
        # Convert all IDs to strings for display, but keep original format for queries
        property_ids_clean = [str(pid) for pid in property_ids]
        
        # Also prepare UUID objects for database queries (Django handles both, but being explicit)
        from uuid import UUID
        property_uuids = []
        for pid in property_ids:
            try:
                if isinstance(pid, str):
                    property_uuids.append(UUID(pid))
                else:
                    property_uuids.append(pid)
            except (ValueError, TypeError):
                # If UUID conversion fails, use original
                property_uuids.append(pid)
        
        # Perform deletions in a transaction
        # Use the same pattern as PropertyViewSet.destroy for consistency
        from django.db import connection
        
        try:
            # Use a top-level transaction, but use savepoints for each property
            # This way if one property fails, it doesn't abort the entire transaction
            with transaction.atomic():
                for prop_id_str in property_ids_clean:
                    # Use a savepoint for each property deletion
                    # If this property fails, we rollback only this savepoint, not the whole transaction
                    savepoint_id = transaction.savepoint()
                    try:
                        # Get property - Django ORM handles both string and UUID
                        prop = Property.objects.get(id=prop_id_str)
                        prop_id = str(prop.id)
                        prop_title = prop.title
                        prop_uuid = prop.id  # Keep UUID for potential raw SQL fallback
                        
                        print(f"[BULK DELETE] Processing property: {prop_id} - {prop_title}")
                        
                        # Use raw SQL deletion directly to avoid Django ORM issues with missing tables
                        # This bypasses all CASCADE checks and table existence issues
                        # This is more reliable and doesn't depend on CASCADE relationships or table existence
                        try:
                            print(f"[BULK DELETE]   Deleting via raw SQL (reliable method)...")
                            with connection.cursor() as cursor:
                                # Delete all related objects via raw SQL first (in correct order to avoid constraint issues)
                                # Order matters: delete dependent objects before the main object
                                try:
                                    cursor.execute("DELETE FROM listings_propertyreview WHERE property_id = %s", [prop_uuid])
                                except Exception:
                                    pass  # Table might not exist
                                
                                try:
                                    cursor.execute("DELETE FROM listings_contact WHERE property_id = %s", [prop_uuid])
                                except Exception:
                                    pass
                                
                                try:
                                    cursor.execute("DELETE FROM listings_propertyview WHERE property_id = %s", [prop_uuid])
                                except Exception:
                                    pass
                                
                                try:
                                    cursor.execute("DELETE FROM listings_favorite WHERE property_id = %s", [prop_uuid])
                                except Exception:
                                    pass
                                
                                try:
                                    cursor.execute("DELETE FROM listings_propertyimage WHERE property_id = %s", [prop_uuid])
                                except Exception:
                                    pass
                                
                                # Delete the property itself
                                cursor.execute("DELETE FROM listings_property WHERE id = %s", [prop_uuid])
                                
                                # Verify deletion
                                cursor.execute("SELECT COUNT(*) FROM listings_property WHERE id = %s", [prop_uuid])
                                remaining = cursor.fetchone()[0]
                                
                                if remaining > 0:
                                    raise Exception(f"Property {prop_id} still exists after raw SQL deletion")
                                
                                print(f"[BULK DELETE]   ✓ Property deleted via raw SQL: {prop_id}")
                                deleted_count += 1
                                deleted_ids.append(prop_id)
                                # Release savepoint on success
                                transaction.savepoint_commit(savepoint_id)
                                
                        except Exception as sql_error:
                            error_type_sql = type(sql_error).__name__
                            error_str_sql = str(sql_error)
                            print(f"[BULK DELETE]   ✗ Raw SQL deletion failed: {error_type_sql}: {error_str_sql}")
                            
                            # Check if it's a transaction abort error
                            if 'transaction is aborted' in error_str_sql.lower():
                                print(f"[BULK DELETE]   ⚠️ Transaction was aborted - rolling back savepoint and continuing...")
                            
                            import traceback
                            traceback.print_exc()
                            # Rollback this savepoint and continue to next property
                            try:
                                transaction.savepoint_rollback(savepoint_id)
                            except Exception:
                                pass  # Savepoint may already be rolled back
                            not_found_ids.append(prop_id_str)
                            continue  # CRITICAL: Skip to next property
                        
                    except Property.DoesNotExist:
                        print(f"[BULK DELETE]   ✗ Property {prop_id_str} not found (DoesNotExist)")
                        # Rollback savepoint for this property
                        transaction.savepoint_rollback(savepoint_id)
                        not_found_ids.append(prop_id_str)
                        continue  # Skip to next property
                    except Exception as outer_e:
                        # Catch any other unexpected errors in the outer try block
                        import traceback
                        error_trace = traceback.format_exc()
                        error_type = type(outer_e).__name__
                        error_message = str(outer_e)
                        
                        print(f"[BULK DELETE]   ✗ Unexpected error for property {prop_id_str}: {error_type}: {error_message}")
                        print(f"[BULK DELETE]   Traceback: {error_trace}")
                        
                        # Rollback savepoint for this property
                        try:
                            transaction.savepoint_rollback(savepoint_id)
                        except Exception:
                            pass  # Savepoint may already be rolled back
                        
                        not_found_ids.append(prop_id_str)
                        continue  # Continue to next property - don't break the transaction
                
                # Transaction will commit here if no unhandled exceptions
                print(f"[BULK DELETE] Transaction committed: {deleted_count} properties deleted")
                
        except Exception as transaction_error:
            import traceback
            error_trace = traceback.format_exc()
            print(f"[BULK DELETE] Transaction error: {str(transaction_error)}")
            print(f"[BULK DELETE] Traceback: {error_trace}")
            return Response({
                'success': False,
                'message': f'Transaction error during bulk deletion: {str(transaction_error)}',
                'deleted_count': deleted_count
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Clear cache after transaction commits
        try:
            cache.clear()
            print(f"[BULK DELETE] Cache cleared successfully")
        except Exception as cache_error:
            print(f"[BULK DELETE] Warning: Cache clear failed: {str(cache_error)}")
        
        # Final verification AFTER transaction commit: check how many properties were actually deleted
        remaining_count = 0
        try:
            # Wait a moment for transaction to fully commit
            import time
            time.sleep(0.5)
            
            # Use a fresh query to verify deletion - try both string and UUID formats
            # Django should handle both, but try both to be sure
            try:
                remaining_properties = Property.objects.filter(id__in=property_uuids)
                remaining_count = remaining_properties.count()
            except Exception as uuid_error:
                print(f"[BULK DELETE] UUID filter failed, trying string IDs: {str(uuid_error)}")
                remaining_properties = Property.objects.filter(id__in=property_ids_clean)
                remaining_count = remaining_properties.count()
            
            if remaining_count > 0:
                remaining_ids = list(remaining_properties.values_list('id', flat=True))
                print(f"[BULK DELETE] ⚠️  WARNING: {remaining_count} properties still exist after deletion attempt!")
                print(f"[BULK DELETE] Remaining property IDs (first 10): {remaining_ids[:10]}")
                print(f"[BULK DELETE] Expected to delete: {len(property_ids_clean)}, Actually deleted: {deleted_count}, Still remaining: {remaining_count}")
                
                # Try one more time with raw SQL for remaining properties
                print(f"[BULK DELETE] Attempting raw SQL deletion for remaining properties...")
                try:
                    with connection.cursor() as cursor:
                        for remaining_id in remaining_ids[:10]:  # Try first 10 to avoid timeout
                            try:
                                # Delete all related objects
                                cursor.execute("DELETE FROM listings_propertyimage WHERE property_id = %s", [remaining_id])
                                cursor.execute("DELETE FROM listings_favorite WHERE property_id = %s", [remaining_id])
                                cursor.execute("DELETE FROM listings_propertyview WHERE property_id = %s", [remaining_id])
                                cursor.execute("DELETE FROM listings_contact WHERE property_id = %s", [remaining_id])
                                cursor.execute("DELETE FROM listings_propertyreview WHERE property_id = %s", [remaining_id])
                                cursor.execute("DELETE FROM listings_property WHERE id = %s", [remaining_id])
                                print(f"[BULK DELETE]   Raw SQL deleted: {remaining_id}")
                            except Exception as raw_error:
                                print(f"[BULK DELETE]   Raw SQL failed for {remaining_id}: {str(raw_error)}")
                    
                    # Re-check after raw SQL attempt
                    time.sleep(0.5)
                    final_remaining = Property.objects.filter(id__in=property_ids_clean).count()
                    if final_remaining < remaining_count:
                        print(f"[BULK DELETE] Raw SQL helped: {remaining_count - final_remaining} more properties deleted")
                        remaining_count = final_remaining
                except Exception as raw_sql_error:
                    print(f"[BULK DELETE] Raw SQL fallback failed: {str(raw_sql_error)}")
                
                # Return error if any properties remain after all attempts
                if remaining_count > 0:
                    return Response({
                        'success': False,
                        'message': f'Deletion attempted but {remaining_count} properties still exist. This may indicate a database constraint issue. Check backend logs for details.',
                        'deleted_count': deleted_count,
                        'remaining_count': remaining_count,
                        'deleted_ids': deleted_ids[:50],
                        'remaining_ids': remaining_ids[:50]
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            print(f"[BULK DELETE] ✅ Summary: {deleted_count} deleted, {len(not_found_ids)} not found/failed, 0 remaining")
        except Exception as verify_error:
            import traceback
            print(f"[BULK DELETE] Warning: Verification query failed: {str(verify_error)}")
            print(f"[BULK DELETE] Verification traceback: {traceback.format_exc()}")
            # Don't fail the whole operation if verification fails - deletion might have succeeded
        
        # Return success response
        message = f'Successfully deleted {deleted_count} propert{"y" if deleted_count == 1 else "ies"}.'
        if not_found_ids:
            message += f' {len(not_found_ids)} propert{"y" if len(not_found_ids) == 1 else "ies"} not found or could not be deleted.'
        
        return Response({
            'success': True,
            'message': message,
            'deleted_count': deleted_count,
            'deleted_ids': deleted_ids[:100],  # Return first 100 IDs
            'not_found_ids': not_found_ids[:100] if not_found_ids else [],
            'total_requested': len(property_ids)
        }, status=status.HTTP_200_OK)
            
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[BULK DELETE] CRITICAL ERROR: {str(e)}")
        print(f"[BULK DELETE] Traceback: {error_trace}")
        return Response({
            'success': False,
            'message': f'Error during bulk deletion: {str(e)}',
            'deleted_count': deleted_count
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
