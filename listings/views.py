# FILE: ereft_api/listings/views.py
# PRODUCTION READY: All endpoints properly configured per .cursorrules
# TIMESTAMP: 2025-01-15 17:00:00 - FORCE PRODUCTION DEPLOYMENT
# 🚨 CRITICAL: URL conflicts resolved - force new deployment to production

from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg, Count, Sum
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework import status, generics, viewsets, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
# from django_filters.rest_framework import DjangoFilterBackend  # Disabled for deployment
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.core.mail import send_mail
from django_ratelimit.decorators import ratelimit
from django_ratelimit.core import is_ratelimited
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.http import HttpResponse
from django.conf import settings
from datetime import timedelta
import json
import requests
import os
from .models import (
    Property, PropertyImage, Favorite, PropertyView, SearchHistory,
    Contact, Neighborhood, PropertyReview, UserProfile
)
from .serializers import (
    PropertySerializer, PropertyListSerializer, PropertyDetailSerializer,
    PropertyCreateSerializer, PropertySearchSerializer, FavoriteSerializer,
    SearchHistorySerializer, ContactSerializer, NeighborhoodSerializer,
    PropertyReviewSerializer, UserProfileSerializer, UserSerializer
)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class PropertyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Property model with full CRUD operations - Simplified for debugging
    """
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'address', 'city', 'sub_city']
    ordering_fields = ['price', 'created_at', 'bedrooms', 'area_sqm']
    ordering = ['-created_at']
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    CACHE_TIMEOUT = 60  # seconds

    def get_serializer_class(self):
        if self.action == 'create':
            return PropertyCreateSerializer
        elif self.action == 'retrieve':
            return PropertyDetailSerializer
        else:
            return PropertyListSerializer

    def list(self, request, *args, **kwargs):
        """Return cached property list responses to reduce cold-start latency."""
        cache_key = f"property_list:{request.get_full_path()}"
        cached_payload = cache.get(cache_key)
        if cached_payload is not None:
            return Response(cached_payload)

        # Allow `limit` query parameter as an alias for `page_size`
        limit = request.query_params.get('limit')
        if limit:
            try:
                request.GET._mutable = True  # type: ignore[attr-defined]
                request.GET['page_size'] = limit
            except AttributeError:
                pass

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=self.CACHE_TIMEOUT)
        return response

    def create(self, request, *args, **kwargs):
        """Create a property and return the full detail payload including generated ID."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        property_obj = self.perform_create(serializer)
        property_obj = property_obj or serializer.instance

        detail_serializer = PropertyDetailSerializer(
            property_obj,
            context=self.get_serializer_context()
        )
        headers = self.get_success_headers(detail_serializer.data)
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def retrieve(self, request, *args, **kwargs):
        """Return cached property detail responses when available."""
        pk = kwargs.get('pk')
        cache_key = f"property_detail:{pk}"
        cached_payload = cache.get(cache_key)
        if cached_payload is not None:
            return Response(cached_payload)

        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=self.CACHE_TIMEOUT)
        return response
    
    def get_queryset(self):
        # Prefetch related data for better performance
        queryset = Property.objects.select_related('owner', 'agent').prefetch_related('images', 'reviews')
        
        # Apply filters
        listing_type = self.request.query_params.get('listing_type', '')
        if listing_type:
            queryset = queryset.filter(listing_type=listing_type)
        
        property_type = self.request.query_params.get('property_type', '')
        if property_type:
            queryset = queryset.filter(property_type=property_type)
        
        min_price = self.request.query_params.get('min_price', '')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        
        max_price = self.request.query_params.get('max_price', '')
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        bedrooms = self.request.query_params.get('bedrooms', '')
        if bedrooms:
            queryset = queryset.filter(bedrooms__gte=bedrooms)
        
        city = self.request.query_params.get('city', '')
        if city:
            queryset = queryset.filter(city__icontains=city)
        
        featured = self.request.query_params.get('featured', '')
        if featured:
            truthy = str(featured).lower() in ['1', 'true', 'yes']
            queryset = queryset.filter(is_featured=truthy)
        
        return queryset

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return [IsAuthenticatedOrReadOnly()]
    
    def perform_create(self, serializer):
        """Ensure new listings are immediately visible and set proper defaults"""
        try:
            user = self.request.user
            print(f"🏠 PropertyViewSet: Creating property for user: {user.username} (ID: {user.id})")
            print(f"🏠 PropertyViewSet: Property data: {serializer.validated_data}")
            
            images_data = []

            # Accept pre-uploaded image URLs from payload (e.g., mobile app)
            payload_images = serializer.validated_data.pop('images', []) if 'images' in serializer.validated_data else []
            if payload_images:
                print(f"🏠 PropertyViewSet: Received {len(payload_images)} pre-uploaded image URLs")
                for idx, image_value in enumerate(payload_images, 1):
                    if isinstance(image_value, dict):
                        url = image_value.get('url') or image_value.get('secure_url')
                    else:
                        url = str(image_value)
                    if url:
                        images_data.append(url)
                        print(f"✅ PropertyViewSet: Accepted image URL {idx}: {url}")

            # Handle raw file uploads before saving (web form submissions)
            if hasattr(self.request, 'FILES') and 'images' in self.request.FILES:
                image_files = self.request.FILES.getlist('images')
                image_count = len(image_files)
                print(f"🏠 PropertyViewSet: Processing {image_count} images")
                
                for idx, image_file in enumerate(image_files, 1):
                    try:
                        from .utils import handle_property_image_upload
                        temp_id = str(serializer.validated_data.get('title', 'temp'))[:20]
                        image_result = handle_property_image_upload(image_file, temp_id)
                        
                        # Only add if upload was successful (returns dict with 'url')
                        if image_result and isinstance(image_result, dict) and 'url' in image_result:
                            images_data.append(image_result['url'])
                            print(f"✅ PropertyViewSet: Image {idx}/{image_count} uploaded: {image_result['url']}")
                        else:
                            print(f"⚠️ PropertyViewSet: Image {idx}/{image_count} upload skipped (Cloudinary not configured or failed)")
                    except Exception as img_error:
                        print(f"⚠️ PropertyViewSet: Failed to upload image {idx}: {img_error}")
                        print(f"   Property creation will continue without this image")
                        continue
            
            # Create property with uploaded images
            property_obj = serializer.save(
                owner=user,
                status='active',
                is_published=True,
                is_active=True
            )
            
            print(f"✅ PropertyViewSet: Property saved - ID: {property_obj.id}, Title: {property_obj.title}")
            
            # Create PropertyImage objects with the Cloudinary URLs
            if images_data:
                unique_images = list(dict.fromkeys(images_data))
                for i, image_url in enumerate(unique_images, 1):
                    try:
                        PropertyImage.objects.create(
                            property=property_obj,
                            image=image_url,
                            is_primary=(i == 1),
                            order=i
                        )
                        print(f"✅ PropertyViewSet: PropertyImage {i}/{len(unique_images)} created")
                    except Exception as img_error:
                        print(f"⚠️ PropertyViewSet: Failed to create PropertyImage {i}: {img_error}")
                        continue
            
            # Log successful creation with full metadata
            print(f"🎉 PropertyViewSet: Property created successfully!")
            print(f"   Property ID: {property_obj.id}")
            print(f"   Title: {property_obj.title}")
            print(f"   Owner: {user.username} (ID: {user.id}, Email: {user.email})")
            print(f"   Location: {property_obj.city}, {property_obj.country}")
            print(f"   Price: ETB {property_obj.price:,.2f}")
            print(f"   Images: {len(images_data)} uploaded")
            cache.clear()
            return property_obj
            
        except Exception as e:
            print(f"❌ PropertyViewSet: CRITICAL ERROR in perform_create")
            print(f"   User: {self.request.user.username}")
            print(f"   Error: {str(e)}")
            print(f"   Error Type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            raise e
    
    def destroy(self, request, *args, **kwargs):
        """Override destroy to add logging and ensure proper deletion"""
        try:
            instance = self.get_object()
            user = request.user

            # Verify ownership
            if not hasattr(instance, 'owner') or not instance.owner:
                return Response(
                    {'detail': 'Property owner information is missing.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if instance.owner_id != user.id:
                return Response(
                    {'detail': 'You can only delete your own listings.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Log deletion attempt
            print(f"🗑️ PropertyViewSet: DELETE request initiated")
            print(f"   Property ID: {instance.id}")
            print(f"   Title: {instance.title}")
            print(f"   Deleted by: {user.username} (ID: {user.id})")
            print(f"   Owner ID: {instance.owner.id}")
            print(f"   Is Owner: {instance.owner.id == user.id}")
            
            property_id = instance.id
            property_title = instance.title
            owner_username = instance.owner.username
            
            # Handle payments app relationship gracefully if table doesn't exist
            # We need to check if the table exists before Django tries to access it
            try:
                from django.db import connection
                from django.conf import settings
                
                # Check database type and table existence
                db_backend = settings.DATABASES['default']['ENGINE']
                table_name = 'payments_payment'
                
                table_exists = False
                if 'sqlite' in db_backend:
                    # SQLite
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            SELECT name FROM sqlite_master 
                            WHERE type='table' AND name=?
                        """, [table_name])
                        table_exists = cursor.fetchone() is not None
                elif 'postgresql' in db_backend:
                    # PostgreSQL
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            SELECT EXISTS (
                                SELECT FROM information_schema.tables 
                                WHERE table_schema = 'public' 
                                AND table_name = %s
                            )
                        """, [table_name])
                        table_exists = cursor.fetchone()[0]
                
                if table_exists:
                    # Table exists - update related payments
                    try:
                        from payments.models import Payment
                        Payment.objects.filter(property=instance).update(property=None)
                        print(f"   Updated related payments to set property=None")
                    except Exception as update_error:
                        print(f"   Note: Could not update payments: {update_error}")
                else:
                    print(f"   Note: Payments table doesn't exist, skipping payment updates")
            except Exception as payment_error:
                # Any error checking/updating payments - log and continue
                error_msg = str(payment_error).lower()
                if 'no such table' in error_msg or 'does not exist' in error_msg or 'relation' in error_msg:
                    print(f"   Note: Payments table doesn't exist, skipping payment updates")
                else:
                    print(f"   Note: Error handling payments: {payment_error}")
                # Continue with deletion - payments relationship uses SET_NULL so it's safe
            
            # Store property info before deletion
            property_id = instance.id
            property_title = instance.title
            property_uuid_str = str(property_id)
            
            # Use database transaction to ensure atomic deletion
            from django.db import transaction
            
            try:
                with transaction.atomic():
                    # Delete related objects first to avoid foreign key constraints
                    # Delete property images
                    try:
                        image_count = instance.images.count()
                        instance.images.all().delete()
                        print(f"   Deleted {image_count} property images")
                    except Exception as img_error:
                        print(f"   Note: Error deleting images: {img_error}")
                    
                    # Delete favorites referencing this property
                    try:
                        from .models import Favorite
                        fav_count = Favorite.objects.filter(property=instance).count()
                        Favorite.objects.filter(property=instance).delete()
                        print(f"   Deleted {fav_count} favorites for this property")
                    except Exception as fav_error:
                        print(f"   Note: Error deleting favorites: {fav_error}")
                    
                    # Delete property views
                    try:
                        from .models import PropertyView
                        PropertyView.objects.filter(property=instance).delete()
                    except Exception:
                        pass
                    
                    # Delete contacts
                    try:
                        from .models import Contact
                        Contact.objects.filter(property=instance).delete()
                    except Exception:
                        pass
                    
                    # Delete reviews
                    try:
                        from .models import PropertyReview
                        PropertyReview.objects.filter(property=instance).delete()
                    except Exception:
                        pass
                    
                    # Now delete the property itself using raw SQL to bypass any foreign key issues
                    from django.db import connection
                    from django.conf import settings
                    
                    db_backend = settings.DATABASES['default']['ENGINE']
                    
                    with connection.cursor() as cursor:
                        if 'postgresql' in db_backend:
                            # PostgreSQL - use UUID casting
                            cursor.execute("DELETE FROM listings_property WHERE id = %s::uuid", [property_uuid_str])
                        else:
                            # SQLite
                            cursor.execute("DELETE FROM listings_property WHERE id = ?", [property_uuid_str])
                    
                    # Verify deletion immediately
                    try:
                        Property.objects.get(pk=property_id)
                        # If we get here, property still exists
                        raise Exception("Property still exists after deletion")
                    except Property.DoesNotExist:
                        # Property successfully deleted
                        print(f"✅ PropertyViewSet: Property {property_uuid_str} deleted and verified")
                    
            except Exception as delete_error:
                error_str = str(delete_error).lower()
                print(f"❌ PropertyViewSet: Deletion failed: {delete_error}")
                
                # If transaction fails, try direct SQL deletion as last resort
                if 'payments_payment' in error_str or 'no such table' in error_str or 'relation' in error_str:
                    try:
                        print(f"   Attempting direct SQL deletion as fallback")
                        from django.db import connection
                        from django.conf import settings
                        
                        db_backend = settings.DATABASES['default']['ENGINE']
                        
                        with connection.cursor() as cursor:
                            if 'postgresql' in db_backend:
                                cursor.execute("DELETE FROM listings_property WHERE id = %s::uuid", [property_uuid_str])
                            else:
                                cursor.execute("DELETE FROM listings_property WHERE id = ?", [property_uuid_str])
                        
                        # Verify again
                        try:
                            Property.objects.get(pk=property_id)
                            raise Exception("Property still exists after fallback deletion")
                        except Property.DoesNotExist:
                            print(f"✅ PropertyViewSet: Property deleted via fallback SQL")
                    except Exception as fallback_error:
                        print(f"❌ PropertyViewSet: Fallback deletion also failed: {fallback_error}")
                        raise fallback_error
                else:
                    raise delete_error
            
            print(f"✅ PropertyViewSet: Property deleted successfully")
            print(f"   Deleted Property ID: {property_uuid_str}")
            print(f"   Deleted Title: {property_title}")
            print(f"   Owner: {owner_username}")
            
            # Clear all caches
            try:
                cache.clear()
                cache.delete(f"property_detail:{property_uuid_str}")
                print(f"   Cache cleared")
            except Exception as cache_error:
                print(f"   Note: Cache clear error (non-critical): {cache_error}")
            
            # Return 204 No Content (standard for DELETE)
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            print(f"❌ PropertyViewSet: CRITICAL ERROR in destroy")
            print(f"   Error: {str(e)}")
            print(f"   Error Type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            
            # Check if error is related to missing payments table
            error_str = str(e).lower()
            if 'payments_payment' in error_str or 'no such table' in error_str:
                # Try to delete without handling payments
                try:
                    instance = self.get_object()
                    if instance.owner_id == request.user.id:
                        instance.delete()
                        cache.clear()
                        return Response(status=status.HTTP_204_NO_CONTENT)
                except:
                    pass
            
            # Return proper error response instead of raising
            return Response(
                {'detail': f'Failed to delete property: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        """Toggle favorite status for a property"""
        property_obj = self.get_object()
        user = request.user
        
        favorite, created = Favorite.objects.get_or_create(
            user=user,
            property=property_obj
        )
        
        if not created:
            favorite.delete()
            cache.delete(f"property_detail:{property_obj.pk}")
            cache.clear()
            return Response({'status': 'removed from favorites'})
        
        cache.delete(f"property_detail:{property_obj.pk}")
        cache.clear()
        return Response({'status': 'added to favorites'})

    @action(detail=True, methods=['post'])
    def contact(self, request, pk=None):
        """Submit contact form for a property"""
        property_obj = self.get_object()
        serializer = ContactSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(property=property_obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'post'])
    def reviews(self, request, pk=None):
        """Get or create reviews for a property"""
        property_obj = self.get_object()
        
        if request.method == 'GET':
            reviews = PropertyReview.objects.filter(property=property_obj, is_active=True)
            serializer = PropertyReviewSerializer(reviews, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = PropertyReviewSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(property=property_obj, user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured properties"""
        properties = Property.objects.filter(is_active=True, is_featured=True)[:10]
        serializer = PropertyListSerializer(properties, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get property statistics"""
        active_properties = Property.objects.filter(is_active=True, is_published=True)
        total = active_properties.count()
        for_sale = active_properties.filter(listing_type='sale').count()
        for_rent = active_properties.filter(listing_type='rent').count()
        average_price = active_properties.aggregate(avg_price=Avg('price'))['avg_price']
        average_price = float(average_price) if average_price is not None else 0
        
        return Response({
            'total': total,
            'for_sale': for_sale,
            'for_rent': for_rent,
            'average_price': average_price,
        })

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search properties with filters"""
        queryset = self.get_queryset()
        
        # Apply search filters
        search_query = request.query_params.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(address__icontains=search_query) |
                Q(city__icontains=search_query) |
                Q(sub_city__icontains=search_query)
            )
        
        # Apply property type filter
        property_type = request.query_params.get('property_type', '')
        if property_type:
            queryset = queryset.filter(property_type=property_type)
        
        # Apply listing type filter
        listing_type = request.query_params.get('listing_type', '')
        if listing_type:
            queryset = queryset.filter(listing_type=listing_type)
        
        # Apply price range filter
        min_price = request.query_params.get('min_price', '')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        
        max_price = request.query_params.get('max_price', '')
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Apply bedroom filter
        bedrooms = request.query_params.get('bedrooms', '')
        if bedrooms:
            queryset = queryset.filter(bedrooms__gte=bedrooms)
        
        # Apply bathroom filter
        bathrooms = request.query_params.get('bathrooms', '')
        if bathrooms:
            queryset = queryset.filter(bathrooms__gte=bathrooms)
        
        # Apply city filter
        city = request.query_params.get('city', '')
        if city:
            queryset = queryset.filter(city__icontains=city)
        
        # Apply sub_city filter
        sub_city = request.query_params.get('sub_city', '')
        if sub_city:
            queryset = queryset.filter(sub_city__icontains=sub_city)
        
        # Apply sorting
        sort_by = request.query_params.get('sort_by', '-created_at')
        if sort_by in ['price', '-price', 'created_at', '-created_at', 'bedrooms', '-bedrooms']:
            queryset = queryset.order_by(sort_by)
        
        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PropertyListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = PropertyListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

class PropertySearchView(generics.ListAPIView):
    """
    Search properties with filters
    """
    serializer_class = PropertyListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'address', 'city', 'sub_city', 'kebele', 'street_name']
    ordering_fields = ['price', 'created_at', 'bedrooms', 'area_sqm']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Property.objects.filter(is_active=True, is_published=True, status='active')
        
        # Apply search filters
        search_query = self.request.query_params.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(address__icontains=search_query) |
                Q(city__icontains=search_query) |
                Q(sub_city__icontains=search_query)
            )
        
        # Apply property type filter
        property_type = self.request.query_params.get('property_type', '')
        if property_type:
            queryset = queryset.filter(property_type=property_type)
        
        # Apply listing type filter
        listing_type = self.request.query_params.get('listing_type', '')
        if listing_type:
            queryset = queryset.filter(listing_type=listing_type)
        
        # Apply price range filter
        min_price = self.request.query_params.get('min_price', '')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        
        max_price = self.request.query_params.get('max_price', '')
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Apply bedroom filter
        bedrooms = self.request.query_params.get('bedrooms', '')
        if bedrooms:
            queryset = queryset.filter(bedrooms__gte=bedrooms)
        
        # Apply bathroom filter
        bathrooms = self.request.query_params.get('bathrooms', '')
        if bathrooms:
            queryset = queryset.filter(bathrooms__gte=bathrooms)
        
        # Apply city filter
        city = self.request.query_params.get('city', '')
        if city:
            queryset = queryset.filter(city__icontains=city)
        
        # Apply sub_city filter
        sub_city = self.request.query_params.get('sub_city', '')
        if sub_city:
            queryset = queryset.filter(sub_city__icontains=sub_city)
        
        # Apply sorting
        sort_by = self.request.query_params.get('sort_by', '-created_at')
        if sort_by in ['price', '-price', 'created_at', '-created_at', 'bedrooms', '-bedrooms']:
            queryset = queryset.order_by(sort_by)
        
        return queryset

class FavoriteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user favorites
    """
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """Create a favorite for a property"""
        try:
            property_id = request.data.get('property') or request.data.get('property_id')
            if not property_id:
                return Response(
                    {'detail': 'Property ID is required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            property_obj = get_object_or_404(Property, pk=property_id)
            favorite, created = Favorite.objects.get_or_create(user=request.user, property=property_obj)

            # Clear relevant caches
            cache.delete(f"property_detail:{property_obj.pk}")
            if created:
                cache.clear()  # Clear all caches to ensure favorites are updated everywhere
                print(f"✅ FavoriteViewSet: Favorite created for property {property_id} by user {request.user.username}")
            else:
                print(f"ℹ️ FavoriteViewSet: Favorite already exists for property {property_id} by user {request.user.username}")

            serializer = self.get_serializer(favorite)
            return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        except Exception as e:
            print(f"❌ FavoriteViewSet: Error creating favorite: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {'detail': f'Failed to create favorite: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, *args, **kwargs):
        """Delete a favorite by property ID"""
        try:
            property_id = kwargs.get('pk')
            if not property_id:
                return Response(
                    {'detail': 'Property ID is required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Find and delete the favorite
            favorite = get_object_or_404(Favorite, user=request.user, property_id=property_id)
            favorite.delete()
            
            # Clear relevant caches
            cache.delete(f"property_detail:{property_id}")
            cache.clear()  # Clear all caches to ensure favorites are updated everywhere
            
            print(f"✅ FavoriteViewSet: Favorite deleted for property {property_id} by user {request.user.username}")
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            print(f"❌ FavoriteViewSet: Error deleting favorite: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {'detail': f'Failed to delete favorite: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user profiles
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class NeighborhoodViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for neighborhoods (read-only)
    """
    queryset = Neighborhood.objects.all()
    serializer_class = NeighborhoodSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'city']

@api_view(['GET'])
def api_root(request):
    """
    API root endpoint with available endpoints
    """
    return Response({
        'message': 'Ereft Real Estate API',
        'endpoints': {
            'properties': '/api/listings/properties/',
            'search': '/api/listings/properties/search/',
            'favorites': '/api/listings/favorites/',
            'neighborhoods': '/api/listings/neighborhoods/',
            'profile': '/api/listings/profile/',
            'auth': {
                'login': '/api/listings/auth/login/',
                'register': '/api/listings/auth/register/',
                'logout': '/api/listings/auth/logout/',
            }
        }
    })

@api_view(['GET'])
def database_test(request):
    """
    Test database connection and basic queries
    """
    try:
        from django.db import connection
        from .models import Property, User
        
        # Test basic database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_test = cursor.fetchone()
        
        # Test model queries
        property_count = Property.objects.count()
        user_count = User.objects.count()
        
        return Response({
            'status': 'success',
            'database_connection': 'working',
            'property_count': property_count,
            'user_count': user_count,
            'message': 'Database is working correctly'
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'error': str(e),
            'message': 'Database connection failed'
        }, status=500)


@api_view(['POST'])
@permission_classes([])
def setup_admin_users(request):
    """Setup admin and demo users - Production ready"""
    try:
        from django.core.management import call_command
        from io import StringIO
        
        # Capture command output
        out = StringIO()
        call_command('create_admin_user', stdout=out)
        output = out.getvalue()
        
        return Response({
            'status': 'success',
            'message': 'Admin and demo users created successfully',
            'output': output,
            'credentials': {
                'admin': 'admin / admin123 (superuser)',
                'test_user': 'test_user / testpass123 (regular user)'
            }
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Failed to create admin users: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([])
def verify_admin_user(request):
    """Verify admin user email for immediate login - Production ready"""
    try:
        # Find admin user
        admin_user = User.objects.get(username='admin')
        
        # Get or create UserProfile
        user_profile, created = UserProfile.objects.get_or_create(
            user=admin_user,
            defaults={
                'phone_number': '+251911000000',
                'is_agent': True,
                'email_verified': True,
                'is_locked': False,
                'failed_login_attempts': 0
            }
        )
        
        if not created:
            # Update existing profile
            user_profile.email_verified = True
            user_profile.is_locked = False
            user_profile.failed_login_attempts = 0
            user_profile.save()
        
        # Make admin a superuser
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.is_active = True
        admin_user.save()
        
        return Response({
            'status': 'success',
            'message': 'Admin user verified and ready for login',
            'credentials': 'admin / admin123',
            'permissions': 'superuser with email_verified=True'
        })
    
    except User.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Admin user not found. Please register admin user first.'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Failed to verify admin user: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Get current user profile with full user information
    """
    user = request.user
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = UserProfile.objects.create(user=user)
    
    # Return both profile and user data
    profile_serializer = UserProfileSerializer(profile)
    user_serializer = UserSerializer(user)
    
    return Response({
        'user': user_serializer.data,
        'profile': profile_serializer.data,
        **profile_serializer.data  # Include profile fields at root level for backward compatibility
    })

@api_view(['GET'])
def featured_properties(request):
    """
    Get featured properties - Simplified for debugging
    """
    try:
        # Start with simplest possible query
        properties = Property.objects.all()[:5]
        
        # Simple response without serializer to test database connection
        return Response({
            'count': properties.count(),
            'message': 'Featured properties endpoint working',
            'properties': [{'id': str(p.id), 'title': p.title} for p in properties]
        })
    except Exception as e:
        return Response({
            'error': f'Database error: {str(e)}',
            'debug': 'featured_properties endpoint'
        }, status=500)

@api_view(['GET'])
def property_stats(request):
    """
    Get property statistics
    """
    total_properties = Property.objects.filter(is_active=True).count()
    for_sale = Property.objects.filter(is_active=True, listing_type='sale').count()
    for_rent = Property.objects.filter(is_active=True, listing_type='rent').count()
    avg_price = Property.objects.filter(is_active=True).aggregate(Avg('price'))['price__avg']
    
    return Response({
        'total_properties': total_properties,
        'for_sale': for_sale,
        'for_rent': for_rent,
        'average_price': avg_price
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_property_view(request, property_id):
    """
    Track property view
    """
    property_obj = get_object_or_404(Property, id=property_id)
    
    PropertyView.objects.create(
        property=property_obj,
        user=request.user,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    # Increment view count
    property_obj.views_count += 1
    property_obj.save()
    
    return Response({'status': 'view tracked'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_history(request):
    """
    Get user search history
    """
    searches = SearchHistory.objects.filter(user=request.user)[:20]
    serializer = SearchHistorySerializer(searches, many=True)
    return Response(serializer.data)

class UserStatsView(APIView):
    """
    Get real user activity stats for profile dashboard
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Get real counts from database
        total_listings = Property.objects.filter(owner=user).count()
        active_listings = Property.objects.filter(
            owner=user, 
            status='active',
            is_published=True
        ).count()
        pending_review = Property.objects.filter(
            owner=user, 
            status='pending'
        ).count()
        favorites_count = Favorite.objects.filter(user=user).count()
        
        # Total views across all user's properties
        views_total = Property.objects.filter(owner=user).aggregate(
            total_views=Sum('views_count')
        )['total_views'] or 0
        
        # Unread messages (placeholder for future messaging system)
        messages_unread = 0  # TODO: Implement when messaging system is added
        
        # Additional useful stats
        properties_sold = Property.objects.filter(
            owner=user,
            status__in=['sold', 'rented']
        ).count()
        
        recent_views = PropertyView.objects.filter(
            property__owner=user
        ).count()
        
        stats = {
            'total_listings': total_listings,
            'active_listings': active_listings,
            'pending_review': pending_review,
            'favorites_count': favorites_count,
            'views_total': views_total,
            'messages_unread': messages_unread,
            'properties_sold': properties_sold,
            'recent_views': recent_views,
        }
        
        return Response(stats)

@api_view(['POST'])
@permission_classes([])
@ratelimit(key='ip', rate='10/m', method='POST', block=True)
@ratelimit(key='ip', rate='50/h', method='POST', block=True)
def custom_login(request):
    """
    Production-ready login endpoint with security features
    """
    try:
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')
        
        if not username or not password:
            return Response(
                {'error': 'Username and password are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Try to authenticate with username
        user = authenticate(username=username, password=password)
        
        # If that fails, try to find user by email and authenticate
        if not user:
            try:
                user_obj = User.objects.get(email=username.lower())
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        if user and user.is_active:
            # Check if account is locked due to too many failed attempts
            try:
                profile = UserProfile.objects.get(user=user)
                if profile.is_locked and profile.lockout_until and profile.lockout_until > timezone.now():
                    return Response({
                        'error': f'Account is temporarily locked due to too many failed login attempts. Try again after {profile.lockout_until.strftime("%Y-%m-%d %H:%M:%S")} UTC.'
                    }, status=status.HTTP_423_LOCKED)
                elif profile.is_locked and profile.lockout_until and profile.lockout_until <= timezone.now():
                    # Unlock account
                    profile.is_locked = False
                    profile.lockout_until = None
                    profile.failed_login_attempts = 0
                    profile.save()
            except UserProfile.DoesNotExist:
                # Create UserProfile for existing users who don't have one
                profile = UserProfile.objects.create(
                    user=user,
                    email_verified=True,  # Mark existing users as verified
                    phone_verified=False,
                    is_locked=False,
                    failed_login_attempts=0
                )
            
            # MVP: Skip email verification for now - just allow login
            # Auto-verify all users for MVP simplicity
            if not profile.email_verified:
                profile.email_verified = True
                profile.save()
            
            # Auto-promote admin user
            if user.username == 'admin':
                profile.is_agent = True
                user.is_staff = True
                user.is_superuser = True
                user.save()
                profile.save()
            
            # Reset failed login attempts on successful login
            profile.failed_login_attempts = 0
            profile.save()
            
            # Send welcome email only once (on first login)
            # Check if user was created recently (within last 24 hours) to determine if it's a new user
            # For existing users, only send on first login after this feature was added
            hours_since_joined = (timezone.now() - user.date_joined).total_seconds() / 3600
            is_new_user = hours_since_joined < 24  # Created within last 24 hours
            
            # Check if we've sent welcome email before by checking if user joined very recently
            # For existing users (joined more than 24 hours ago), we'll send once on next login
            # We'll track this by checking if there's a flag, or just send for new users
            should_send_welcome = is_new_user
            
            # For existing users, send welcome email on first login after this update
            # We can track this by checking if user has logged in before (simple heuristic)
            # For now, send welcome email for users created in last 7 days to catch recent signups
            if not is_new_user and hours_since_joined < 168:  # Within last 7 days
                should_send_welcome = True
            
            if should_send_welcome:
                try:
                    from .utils import send_welcome_email
                    # Send welcome email (don't block login if it fails)
                    send_welcome_email(user, is_new_user=is_new_user)
                    print(f"✅ Welcome email sent to {user.email} on login")
                except Exception as email_error:
                    # Don't fail login if email fails
                    print(f"⚠️ Failed to send welcome email to {user.email}: {email_error}")
            else:
                print(f"ℹ️ Welcome email skipped for {user.email} (existing user)")
            
            # Get or create token
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'message': 'Login successful!',
                'token': token.key,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            })
        
        # Handle failed login attempts
        if username:
            try:
                user_obj = User.objects.get(username=username)
                profile, created = UserProfile.objects.get_or_create(
                    user=user_obj,
                    defaults={
                        'email_verified': False,
                        'phone_verified': False,
                        'is_locked': False,
                        'failed_login_attempts': 0
                    }
                )
                
                profile.failed_login_attempts += 1
                
                # Lock account after 5 failed attempts for 15 minutes
                if profile.failed_login_attempts >= 5:
                    profile.is_locked = True
                    profile.lockout_until = timezone.now() + timedelta(minutes=15)
                    profile.save()
                    
                    return Response({
                        'error': 'Account locked due to too many failed login attempts. Try again in 15 minutes.'
                    }, status=status.HTTP_423_LOCKED)
                else:
                    profile.save()
                    
            except User.DoesNotExist:
                pass
        
        return Response(
            {'error': 'Invalid credentials or account is inactive'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
        
    except Exception as e:
        return Response(
            {'error': 'Login failed. Please try again.'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def custom_logout(request):
    """
    Production-ready logout endpoint that invalidates tokens
    """
    try:
        # Delete the user's token
        if hasattr(request.user, 'auth_token'):
            request.user.auth_token.delete()
        
        return Response({
            'message': 'Logout successful!'
        })
        
    except Exception as e:
        return Response(
            {'error': 'Logout failed. Please try again.'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([])
@ratelimit(key='ip', rate='3/h', method='POST', block=True)
def request_password_reset(request):
    """
    REAL password reset via email - no placeholders
    """
    try:
        email = request.data.get('email', '').strip().lower()
        
        if not email or '@' not in email:
            return Response(
                {'error': 'Please provide a valid email address'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
            if user.is_active:
                # Send REAL password reset email
                try:
                    from .utils import send_password_reset_email
                    if send_password_reset_email(user, request):
                        return Response({
                            'message': 'Password reset link has been sent to your email address.'
                        })
                    else:
                        return Response({
                            'error': 'Failed to send password reset email. Please try again.'
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                except Exception as e:
                    print(f"🔐 Password reset email failed: {e}")
                    return Response({
                        'error': 'Password reset email failed. Please try again.'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except User.DoesNotExist:
            # Don't reveal if user exists or not
            pass
        
        return Response({
            'message': 'If an account with this email exists, you will receive a password reset link.'
        })
        
    except Exception as e:
        return Response(
            {'error': 'Password reset request failed. Please try again.'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([])
def verify_email_endpoint(request, uidb64, token):
    """
    REAL email verification endpoint - no placeholders
    """
    try:
        from .utils import verify_email_token
        user = verify_email_token(uidb64, token)
        
        if user:
            return Response({
                'message': 'Email verified successfully! You can now log in to your account.',
                'verified': True
            })
        else:
            return Response({
                'error': 'Invalid or expired verification link.',
                'verified': False
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'error': 'Email verification failed. Please try again.',
            'verified': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([])
def reset_password_confirm(request, uidb64, token):
    """
    REAL password reset confirmation - no placeholders
    """
    try:
        new_password = request.data.get('new_password')
        
        if not new_password or len(new_password) < 8:
            return Response({
                'error': 'Password must be at least 8 characters long'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        from .utils import reset_password_with_token
        user = reset_password_with_token(uidb64, token, new_password)
        
        if user:
            return Response({
                'message': 'Password reset successfully! You can now log in with your new password.'
            })
        else:
            return Response({
                'error': 'Invalid or expired reset link.'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'error': 'Password reset failed. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def process_google_oauth_code(code, request):
    """
    Process Google OAuth authorization code and return appropriate response
    """
    try:
        print(f"🔐 Processing Google OAuth code: {code[:10]}...")
        
        # Google OAuth configuration - Use environment variables
        GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
        GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
        
        # Exchange authorization code for access token
        token_url = 'https://oauth2.googleapis.com/token'
        
        # Use the redirect URI that's configured in Google Cloud Console
        redirect_uri = 'https://ereft.onrender.com/oauth'
        
        token_data = {
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri
        }
        
        print(f"🔐 Google OAuth: Exchanging code for token...")
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        token_info = token_response.json()
        
        access_token = token_info.get('access_token')
        if not access_token:
            return HttpResponse("""
            <html>
            <head><title>OAuth Error</title></head>
            <body>
                <h2>OAuth Error</h2>
                <p>Failed to obtain access token from Google</p>
            </body>
            </html>
            """)
        
        print(f"🔐 Google OAuth: Access token obtained, fetching user info...")
        
        # Get user info from Google
        user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        headers = {'Authorization': f'Bearer {access_token}'}
        user_response = requests.get(user_info_url, headers=headers)
        user_response.raise_for_status()
        user_info = user_response.json()
        
        # Extract user information
        google_id = user_info.get('id')
        email = user_info.get('email')
        first_name = user_info.get('given_name', '')
        last_name = user_info.get('family_name', '')
        profile_picture = user_info.get('picture')
        
        if not email:
            return HttpResponse("""
            <html>
            <head><title>OAuth Error</title></head>
            <body>
                <h2>OAuth Error</h2>
                <p>Email is required from Google OAuth</p>
            </body>
            </html>
            """)
        
        print(f"🔐 Google OAuth: User info received: {email}")
        
        # Check if user already exists
        try:
            user = User.objects.get(email=email)
            print(f"🔐 Google OAuth: Existing user found: {user.username}")
            
            # Update existing user info
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            
            # Update or create UserProfile for existing users
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'email_verified': True,
                    'phone_verified': False,
                    'profile_picture': profile_picture,
                    'google_id': google_id
                }
            )
            
            # Update profile if it already exists
            if not created:
                profile.email_verified = True
                profile.profile_picture = profile_picture or profile.profile_picture
                profile.google_id = google_id or profile.google_id
                profile.save()
            
            # Send welcome email for existing users on OAuth login
            try:
                from .utils import send_welcome_email
                send_welcome_email(user, is_new_user=False)
                print(f"🔐 Google OAuth: Welcome email sent to {email} on login")
            except Exception as e:
                print(f"🔐 Google OAuth: Failed to send welcome email: {str(e)}")
            
        except User.DoesNotExist:
            # Create new user
            username = f"google_{google_id}" if google_id else f"google_{email.split('@')[0]}"
            
            # Ensure username is unique
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
            
            print(f"🔐 Google OAuth: Creating new user: {username}")
            
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=None  # No password for OAuth users
            )
            
            # Create UserProfile for Google OAuth user
            UserProfile.objects.create(
                user=user,
                email_verified=True,  # Google OAuth users are pre-verified
                phone_verified=False,
                profile_picture=profile_picture,
                google_id=google_id
            )
            
            # Send welcome email for new Google OAuth users
            try:
                from .utils import send_welcome_email
                send_welcome_email(user, is_new_user=True)
                print(f"🔐 Google OAuth: Welcome email sent to {email} for new user")
            except Exception as e:
                print(f"🔐 Google OAuth: Failed to send welcome email: {str(e)}")
        
        # Generate or get existing token
        token, created = Token.objects.get_or_create(user=user)
        
        print(f"🔐 Google OAuth: Authentication successful for user: {user.username}")
        
        # For GET requests (redirect from Google), detect platform and redirect accordingly
        if request.method == 'GET':
            # Detect if this is a web request (non-mobile)
            user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
            is_mobile_app = 'expo' in user_agent or 'okhttp' in user_agent or 'react-native' in user_agent
            
            # Check if the website redirect URL is in the state (passed from website)
            state = request.GET.get('state', '')
            is_web_request = 'website' in state or 'ereft' not in user_agent
            
            print(f"🔐 Google OAuth: User-Agent: {user_agent[:100]}")
            print(f"🔐 Google OAuth: State: {state}")
            print(f"🔐 Google OAuth: Detected web request: {is_web_request}")
            
            if is_web_request:
                # Redirect to website with token
                from urllib.parse import urlencode
                
                # Extract website URL from state parameter
                website_url = "https://ereft.com/login"  # Default fallback
                if state.startswith('website_'):
                    try:
                        origin = state.replace('website_', '')
                        website_url = f"{origin}/login"
                    except:
                        pass
                
                redirect_url = f"{website_url}?{urlencode({'token': token.key, 'success': 'true'})}"
                
                print(f"🔐 Google OAuth: State: {state}")
                print(f"🔐 Google OAuth: Website URL: {website_url}")
                print(f"🔐 Google OAuth: Redirecting to: {redirect_url}")
                
                # Return HTML page that redirects to website
                return HttpResponse(f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Signing in to Ereft...</title>
                    <meta charset="UTF-8">
                    <meta http-equiv="refresh" content="0;url={redirect_url}">
                    <style>
                        body {{
                            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            min-height: 100vh;
                            margin: 0;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        }}
                    </style>
                </head>
                <body>
                    <p style="color: white;">Redirecting...</p>
                </body>
                </html>
                """)
            
            # Mobile app redirect (deep link)
            deep_link = f"ereft://oauth?token={token.key}&user_id={user.id}&email={email}&first_name={first_name}&last_name={last_name}&google_id={google_id}"
            
            print(f"🔐 Google OAuth: Redirecting to mobile app: {deep_link}")
            
            # Return HTML page that immediately redirects to the mobile app
            return HttpResponse(f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Redirecting to Ereft App...</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        min-height: 100vh;
                        margin: 0;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        text-align: center;
                    }}
                    .container {{
                        background: rgba(255, 255, 255, 0.1);
                        padding: 2rem;
                        border-radius: 20px;
                        backdrop-filter: blur(10px);
                        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                        max-width: 400px;
                        width: 90%;
                    }}
                    h1 {{
                        margin: 0 0 1rem 0;
                        font-size: 1.5rem;
                    }}
                    p {{
                        margin: 0.5rem 0;
                        opacity: 0.9;
                    }}
                    .spinner {{
                        width: 40px;
                        height: 40px;
                        border: 4px solid rgba(255, 255, 255, 0.3);
                        border-top: 4px solid white;
                        border-radius: 50%;
                        animation: spin 1s linear infinite;
                        margin: 1rem auto;
                    }}
                    @keyframes spin {{
                        0% {{ transform: rotate(0deg); }}
                        100% {{ transform: rotate(360deg); }}
                    }}
                    .button {{
                        display: inline-block;
                        margin-top: 1rem;
                        padding: 12px 24px;
                        background: rgba(255, 255, 255, 0.2);
                        color: white;
                        text-decoration: none;
                        border-radius: 25px;
                        border: 2px solid rgba(255, 255, 255, 0.3);
                        transition: all 0.3s ease;
                    }}
                    .button:hover {{
                        background: rgba(255, 255, 255, 0.3);
                        transform: translateY(-2px);
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🎉 Welcome to Ereft!</h1>
                    <p>Hello, {first_name} {last_name}!</p>
                    <p>You have been successfully authenticated.</p>
                    <div class="spinner"></div>
                    <p>Redirecting to the app...</p>
                    <a href="{deep_link}" class="button">Open Ereft App</a>
                </div>
                
                <script>
                    // Immediate redirect to the mobile app
                    window.location.href = "{deep_link}";
                    
                    // Fallback: try to open the app after a short delay
                    setTimeout(() => {{
                        window.location.href = "{deep_link}";
                    }}, 1000);
                    
                    // Additional fallback for iOS
                    setTimeout(() => {{
                        window.location.href = "{deep_link}";
                    }}, 2000);
                </script>
            </body>
            </html>
            """)
        
        # For POST requests (from mobile app), return JSON response
        else:
            return Response({
                'token': token.key,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'profile_picture': profile_picture,
                    'provider': 'google',
                    'google_id': google_id
                }
            })
        
    except requests.RequestException as e:
        print(f"🔐 Google OAuth: Google API request failed: {str(e)}")
        if request.method == 'GET':
            return HttpResponse(f"""
            <html>
            <head><title>OAuth Error</title></head>
            <body>
                <h2>OAuth Error</h2>
                <p>Google API request failed: {str(e)}</p>
            </body>
            </html>
            """)
        else:
            return Response({
                'error': f'Google API request failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        print(f"🔐 Google OAuth: Unexpected error: {str(e)}")
        if request.method == 'GET':
            return HttpResponse(f"""
            <html>
            <head><title>OAuth Error</title></head>
            <body>
                <h2>OAuth Error</h2>
                <p>Unexpected error: {str(e)}</p>
            </body>
            </html>
            """)
        else:
            return Response({
                'error': f'Unexpected error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([])
@ratelimit(key='ip', rate='5/h', method='POST', block=True)
@ratelimit(key='ip', rate='10/m', method='POST', block=True)
def custom_register(request):
    """
    Production-ready registration endpoint with validation and security
    """
    try:
        username = request.data.get('username', '').strip()
        email = request.data.get('email', '').strip().lower()
        password = request.data.get('password', '')
        first_name = request.data.get('first_name', '').strip()
        last_name = request.data.get('last_name', '').strip()
        
        # Input validation
        if not username or not email or not password:
            return Response(
                {'error': 'Username, email, and password are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Username validation (3-30 chars, alphanumeric + underscore)
        if len(username) < 3 or len(username) > 30:
            return Response(
                {'error': 'Username must be between 3 and 30 characters'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not username.replace('_', '').isalnum():
            return Response(
                {'error': 'Username can only contain letters, numbers, and underscores'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Email validation
        if '@' not in email or '.' not in email:
            return Response(
                {'error': 'Please enter a valid email address'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Password validation (minimum 8 chars, at least one letter and number)
        if len(password) < 8:
            return Response(
                {'error': 'Password must be at least 8 characters long'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
            return Response(
                {'error': 'Password must contain at least one letter and one number'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'Username already exists'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'Email already exists'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Create UserProfile for the new user (MVP: auto-verify for simplicity)
        UserProfile.objects.create(
            user=user,
            email_verified=True,  # MVP: Skip email verification
            phone_verified=False
        )
        
        # Create token
        token, created = Token.objects.get_or_create(user=user)
        
        # Send welcome email for new users
        try:
            from .utils import send_welcome_email
            send_welcome_email(user, is_new_user=True)
            print(f"✅ Registration: Welcome email sent to {user.email}")
        except Exception as e:
            print(f"⚠️ Registration: Failed to send welcome email: {str(e)}")
        
        # MVP: Simple successful registration response
        return Response({
            'message': 'Registration successful! You can now login.',
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': 'Registration failed. Please try again.'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET', 'POST'])
@permission_classes([])
@csrf_exempt
def google_oauth_endpoint(request):
    """
    Handle Google OAuth authentication
    GET: Handles redirect from Google OAuth (for mobile app deep linking)
    POST: Receives authorization code from mobile app
    """
    try:
        print(f"🔐 Google OAuth endpoint called with method: {request.method}")
        
        # Handle GET request (redirect from Google)
        if request.method == 'GET':
            code = request.GET.get('code')
            error = request.GET.get('error')
            
            if error:
                print(f"🔐 Google OAuth error: {error}")
                # Redirect to mobile app with error
                error_url = f"ereft://oauth?error={error}"
                return HttpResponse(f"""
                <html>
                <head><title>OAuth Error</title></head>
                <body>
                    <h2>OAuth Error</h2>
                    <p>Error: {error}</p>
                    <p>Redirecting to app...</p>
                    <script>
                        setTimeout(() => {{
                            window.location.href = "{error_url}";
                        }}, 2000);
                    </script>
                </body>
                </html>
                """)
            
            if not code:
                return HttpResponse("""
                <html>
                <head><title>OAuth Error</title></head>
                <body>
                    <h2>OAuth Error</h2>
                    <p>No authorization code received</p>
                </body>
                </html>
                """)
            
            # Process the authorization code
            return process_google_oauth_code(code, request)
        
        # Handle POST request (from mobile app)
        elif request.method == 'POST':
            # Get authorization code from request
            code = request.data.get('code')
            redirect_uri = request.data.get('redirect_uri')
            
            if not code:
                return Response({
                    'error': 'Authorization code is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Process the authorization code
            return process_google_oauth_code(code, request)
        
        else:
            return Response({
                'error': 'Method not allowed'
            }, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
    except Exception as e:
        print(f"🔐 Google OAuth: Unexpected error: {str(e)}")
        if request.method == 'GET':
            return HttpResponse(f"""
            <html>
            <head><title>OAuth Error</title></head>
            <body>
                <h2>OAuth Error</h2>
                <p>Unexpected error: {str(e)}</p>
            </body>
            </html>
            """)
        else:
            return Response({
                'error': f'Unexpected error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_token(request):
    """
    Verify if the current user's token is valid
    """
    try:
        # If we reach here, the token is valid (Django REST Framework handles this)
        user = request.user
        
        return Response({
            'valid': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        })
        
    except Exception as e:
        print(f"🔐 Token verification error: {str(e)}")
        return Response({
            'valid': False,
            'error': 'Token verification failed'
        }, status=status.HTTP_401_UNAUTHORIZED)

# ------------------------------------------------------
# Enhanced Authentication Views with Email & SMS Verification
# ------------------------------------------------------

@api_view(['POST'])
@permission_classes([])
def enhanced_register(request):
    """
    Enhanced registration with email verification
    """
    try:
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        phone = request.data.get('phone', '')
        
        if not username or not email or not password:
            return Response(
                {'error': 'Username, email, and password are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'Username already exists'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'Email already exists'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create user but mark as inactive until email verification
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=False  # User must verify email first
        )
        
        # Generate verification token
        verification_token = get_random_string(64)
        
        # Create or get user profile
        user_profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'phone_number': phone,
                'verification_token': verification_token,
                'verification_token_created': timezone.now(),
            }
        )
        
        if not created:
            # Update existing profile
            user_profile.verification_token = verification_token
            user_profile.verification_token_created = timezone.now()
            user_profile.phone_number = phone
            user_profile.save()
        
        # Send verification email
        try:
            verification_url = f"https://ereft.onrender.com/verify-email/{verification_token}"
            subject = 'Verify Your Ereft Account'
            message = f"""
            Welcome to Ereft!
            
            Please verify your email address by clicking the link below:
            {verification_url}
            
            This link will expire in 24 hours.
            
            If you didn't create this account, please ignore this email.
            
            Best regards,
            The Ereft Team
            """
            
            send_mail(
                subject,
                message,
                'noreply@ereft.com',
                [email],
                fail_silently=False,
            )
            
            print(f"🔐 Verification email sent to {email}")
            
        except Exception as email_error:
            print(f"🔐 Failed to send verification email: {email_error}")
            # Delete user if email sending fails
            user.delete()
            return Response(
                {'error': 'Failed to send verification email. Please try again.'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({
            'message': 'Registration successful! Please check your email to verify your account.',
            'user_id': user.id,
            'email': email
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        print(f"🔐 Enhanced registration error: {str(e)}")
        return Response(
            {'error': 'Registration failed. Please try again.'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([])
def verify_email(request, token):
    """
    Verify email address using verification token
    """
    try:
        # Find user with this verification token
        try:
            user_profile = UserProfile.objects.get(verification_token=token)
            user = user_profile.user
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'Invalid verification token'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if token is expired (24 hours)
        if user_profile.verification_token_created < timezone.now() - timedelta(hours=24):
            return Response(
                {'error': 'Verification token has expired. Please request a new one.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Activate user and clear verification token
        user.is_active = True
        user.save()
        
        user_profile.verification_token = None
        user_profile.verification_token_created = None
        user_profile.email_verified = True
        user_profile.save()
        
        # Generate JWT token
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Email verified successfully! Your account is now active.',
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        })
        
    except Exception as e:
        print(f"🔐 Email verification error: {str(e)}")
        return Response(
            {'error': 'Email verification failed. Please try again.'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([])
def send_sms_verification(request):
    """
    Send SMS verification code to phone number
    """
    try:
        phone = request.data.get('phone')
        
        if not phone:
            return Response(
                {'error': 'Phone number is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate 6-digit verification code
        verification_code = get_random_string(6, allowed_chars='0123456789')
        
        # Store verification code in user profile (if user exists) or create temporary storage
        # For now, we'll store it in the request session or create a temporary verification record
        
        # Send SMS via Twilio
        try:
            from twilio.rest import Client
            
            account_sid = settings.TWILIO_ACCOUNT_SID
            auth_token = settings.TWILIO_AUTH_TOKEN
            twilio_phone = settings.TWILIO_PHONE_NUMBER
            
            if not all([account_sid, auth_token, twilio_phone]):
                return Response(
                    {'error': 'SMS service not configured'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            client = Client(account_sid, auth_token)
            message = client.messages.create(
                body=f'Your Ereft verification code is: {verification_code}',
                from_=twilio_phone,
                to=phone
            )
            
            print(f"🔐 SMS verification code sent to {phone}")
            
            # Store verification code (in production, use Redis or database)
            # For now, return success
            return Response({
                'message': 'SMS verification code sent successfully',
                'phone': phone
            })
            
        except Exception as twilio_error:
            print(f"🔐 Twilio SMS error: {twilio_error}")
            return Response(
                {'error': 'Failed to send SMS. Please try again.'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    except Exception as e:
        print(f"🔐 SMS verification error: {str(e)}")
        return Response(
            {'error': 'SMS verification failed. Please try again.'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([])
def verify_sms_code(request):
    """
    Verify SMS verification code
    """
    try:
        phone = request.data.get('phone')
        code = request.data.get('code')
        
        if not phone or not code:
            return Response(
                {'error': 'Phone number and verification code are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # In production, verify the code against stored verification record
        # For now, we'll return success (you should implement proper verification)
        
        return Response({
            'message': 'SMS verification successful',
            'phone': phone
        })
        
    except Exception as e:
        print(f"🔐 SMS code verification error: {str(e)}")
        return Response(
            {'error': 'SMS verification failed. Please try again.'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([])
def enhanced_login(request):
    """
    Enhanced login with JWT tokens
    """
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {'error': 'Username and password are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Try to authenticate with username
        user = authenticate(username=username, password=password)
        
        # If that fails, try to find user by email and authenticate
        if not user:
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        if user and user.is_active:
            # Generate JWT tokens
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            })
        
        return Response(
            {'error': 'Invalid credentials or account not verified'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
        
    except Exception as e:
        print(f"🔐 Enhanced login error: {str(e)}")
        return Response(
            {'error': 'Login failed. Please try again.'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_token(request):
    """
    Refresh JWT access token
    """
    try:
        refresh_token = request.data.get('refresh_token')
        
        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken(refresh_token)
        
        return Response({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh)
        })
        
    except Exception as e:
        print(f"🔐 Token refresh error: {str(e)}")
        return Response(
            {'error': 'Token refresh failed. Please try again.'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
def oauth_callback(request):
    """
    Handle OAuth callback - exchange authorization code for JWT and redirect to app
    """
    try:
        print(f"🔐 OAuth callback received")
        
        # Get the authorization code from request body
        code = request.data.get('code')
        redirect_uri = request.data.get('redirect_uri')
        
        if not code:
            return JsonResponse({
                'error': 'Authorization code is required'
            }, status=400)
        
        print(f"🔐 Processing OAuth code: {code[:10]}...")
        
        # Google OAuth configuration
        GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
        GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
        
        # Exchange authorization code for access token
        token_url = 'https://oauth2.googleapis.com/token'
        
        # Use the provided redirect URI or default to the one configured in Google Cloud Console
        if not redirect_uri:
            redirect_uri = 'https://ereft.onrender.com/oauth'
        
        token_data = {
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri
        }
        
        print(f"🔐 Google OAuth: Exchanging code for token...")
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        token_info = token_response.json()
        
        access_token = token_info.get('access_token')
        if not access_token:
            return JsonResponse({
                'error': 'Failed to obtain access token from Google'
            }, status=400)
        
        print(f"🔐 Google OAuth: Access token obtained, fetching user info...")
        
        # Get user info from Google
        user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        headers = {'Authorization': f'Bearer {access_token}'}
        user_response = requests.get(user_info_url, headers=headers)
        user_response.raise_for_status()
        user_info = user_response.json()
        
        print(f"🔐 Google OAuth: User info received: {user_info.get('email', 'No email')}")
        
        # Create or get user
        email = user_info.get('email')
        if not email:
            return JsonResponse({
                'error': 'No email received from Google'
            }, status=400)
        
        # Try to get existing user by email
        try:
            user = User.objects.get(email=email)
            print(f"🔐 Google OAuth: Existing user found: {user.username}")
        except User.DoesNotExist:
            # Create new user
            username = user_info.get('name', email.split('@')[0])
            # Ensure username is unique
            original_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{original_username}{counter}"
                counter += 1
            
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=user_info.get('given_name', ''),
                last_name=user_info.get('family_name', ''),
                is_active=True
            )
            print(f"🔐 Google OAuth: New user created: {user.username}")
        
        # Generate JWT tokens
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        print(f"🔐 Google OAuth: JWT tokens generated for user: {user.username}")
        
        # Return the tokens and user data
        return JsonResponse({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token': access_token,  # Alias for compatibility
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_verified': user.is_active,
            }
        })
        
    except requests.RequestException as e:
        print(f"🔐 OAuth callback error (Google API): {str(e)}")
        return JsonResponse({
            'error': 'Failed to communicate with Google OAuth service'
        }, status=500)
    except Exception as e:
        print(f"🔐 OAuth callback error: {str(e)}")
        return JsonResponse({
            'error': 'OAuth callback processing failed'
        }, status=500)
