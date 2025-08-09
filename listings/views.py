# FILE: ereft_api/listings/views.py

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
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
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
    ViewSet for Property model with full CRUD operations
    """
    queryset = Property.objects.filter(is_active=True, is_published=True, status='active')
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['property_type', 'listing_type', 'city', 'sub_city', 'kebele', 'bedrooms', 'bathrooms', 'status']
    search_fields = ['title', 'description', 'address', 'city', 'sub_city', 'kebele', 'street_name']
    ordering_fields = ['price', 'created_at', 'bedrooms', 'area_sqm']
    ordering = ['-created_at']
    parser_classes = (MultiPartParser, FormParser)

    def get_serializer_class(self):
        if self.action == 'create':
            return PropertyCreateSerializer
        elif self.action == 'retrieve':
            return PropertyDetailSerializer
        else:
            return PropertyListSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return [IsAuthenticatedOrReadOnly()]
    
    def perform_create(self, serializer):
        """Ensure new listings are immediately visible and set proper defaults"""
        serializer.save(
            owner=self.request.user,
            status='active',
            is_published=True,
            is_active=True
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
            return Response({'status': 'removed from favorites'})
        
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
            reviews = property_obj.reviews.all()
            serializer = PropertyReviewSerializer(reviews, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = PropertyReviewSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(property=property_obj, user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PropertySearchView(generics.ListAPIView):
    """
    Advanced property search with filters
    """
    serializer_class = PropertyListSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Property.objects.filter(is_active=True)
        
        # Get search parameters
        query = self.request.query_params.get('query', None)
        property_type = self.request.query_params.get('property_type', None)
        listing_type = self.request.query_params.get('listing_type', None)
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        min_bedrooms = self.request.query_params.get('min_bedrooms', None)
        max_bedrooms = self.request.query_params.get('max_bedrooms', None)
        min_bathrooms = self.request.query_params.get('min_bathrooms', None)
        max_bathrooms = self.request.query_params.get('max_bathrooms', None)
        city = self.request.query_params.get('city', None)
        state = self.request.query_params.get('state', None)
        has_garage = self.request.query_params.get('has_garage', None)
        has_pool = self.request.query_params.get('has_pool', None)
        sort_by = self.request.query_params.get('sort_by', '-created_at')
        
        # Apply filters
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(address__icontains=query) |
                Q(city__icontains=query) |
                Q(state__icontains=query)
            )
        
        if property_type:
            queryset = queryset.filter(property_type=property_type)
        
        if listing_type:
            queryset = queryset.filter(listing_type=listing_type)
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        if min_bedrooms:
            queryset = queryset.filter(bedrooms__gte=min_bedrooms)
        
        if max_bedrooms:
            queryset = queryset.filter(bedrooms__lte=max_bedrooms)
        
        if min_bathrooms:
            queryset = queryset.filter(bathrooms__gte=min_bathrooms)
        
        if max_bathrooms:
            queryset = queryset.filter(bathrooms__lte=max_bathrooms)
        
        if city:
            queryset = queryset.filter(city__icontains=city)
        
        if state:
            queryset = queryset.filter(state__icontains=state)
        
        if has_garage == 'true':
            queryset = queryset.filter(has_garage=True)
        
        if has_pool == 'true':
            queryset = queryset.filter(has_pool=True)
        
        # Save search history if user is authenticated
        if self.request.user.is_authenticated and query:
            SearchHistory.objects.create(
                user=self.request.user,
                query=query,
                filters=self.request.query_params.dict()
            )
        
        # Apply sorting
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
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['city']
    search_fields = ['name', 'city']

@api_view(['GET'])
def api_root(request):
    """
    API root endpoint with available endpoints
    """
    return Response({
        'message': 'Ereft Real Estate API',
        'endpoints': {
            'properties': '/api/properties/',
            'search': '/api/properties/search/',
            'favorites': '/api/favorites/',
            'neighborhoods': '/api/neighborhoods/',
            'profile': '/api/profile/',
            'auth': {
                'login': '/api/auth/login/',
                'register': '/api/auth/register/',
                'logout': '/api/auth/logout/',
            }
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Get current user profile
    """
    user = request.user
    try:
        profile = user.profile
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = UserProfile.objects.create(user=user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

@api_view(['GET'])
def featured_properties(request):
    """
    Get featured properties
    """
    properties = Property.objects.filter(is_active=True, is_featured=True)[:10]
    serializer = PropertyListSerializer(properties, many=True, context={'request': request})
    return Response(serializer.data)

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
def custom_login(request):
    """
    Custom login endpoint that works with email or username
    """
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
    
    if user:
        # Get or create token
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        })
    
    return Response(
        {'error': 'Invalid credentials'}, 
        status=status.HTTP_401_UNAUTHORIZED
    )

@api_view(['POST'])
@permission_classes([])
def custom_register(request):
    """
    Custom registration endpoint
    """
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    first_name = request.data.get('first_name', '')
    last_name = request.data.get('last_name', '')
    
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
    
    # Create user
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )
    
    # Create token
    token, created = Token.objects.get_or_create(user=user)
    
    return Response({
        'token': token.key,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
    }, status=status.HTTP_201_CREATED)
