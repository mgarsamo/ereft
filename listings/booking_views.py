"""
Booking API Views for managing booking requests and approvals
"""
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from .models import Property, Booking, Conversation, Message
from .serializers import BookingSerializer, ConversationSerializer, MessageSerializer
from django.utils import timezone


def is_admin(user):
    """Check if user is admin"""
    if not user.is_authenticated:
        return False
    admin_emails = ['admin@ereft.com', 'melaku.garsamo@gmail.com', 'cb.garsamo@gmail.com', 'lydiageleta45@gmail.com']
    return user.is_superuser or user.is_staff or (user.email and user.email.lower() in [e.lower() for e in admin_emails])


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def bookings_list_create(request):
    """
    GET: List all bookings (filtered by status if provided)
    POST: Create a new booking request
    """
    if request.method == 'GET':
        status_filter = request.query_params.get('status')
        bookings = Booking.objects.all()
        
        # Admins can see all bookings, users only see their own
        if not is_admin(request.user):
            bookings = bookings.filter(guest=request.user)
        
        if status_filter:
            bookings = bookings.filter(status=status_filter)
        
        serializer = BookingSerializer(bookings, many=True, context={'request': request})
        return Response({
            'results': serializer.data,
            'count': len(serializer.data)
        })
    
    elif request.method == 'POST':
        property_id = request.data.get('property')
        if not property_id:
            return Response({'detail': 'Property ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            property_obj = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return Response({'detail': 'Property not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Create booking
        booking_data = {
            'property': property_obj,
            'guest': request.user if request.user.is_authenticated else None,
            'guest_name': request.data.get('guest_name', request.user.get_full_name() if request.user.is_authenticated else ''),
            'guest_email': request.data.get('guest_email', request.user.email if request.user.is_authenticated else ''),
            'guest_phone': request.data.get('guest_phone', ''),
            'check_in_date': request.data.get('check_in_date'),
            'check_out_date': request.data.get('check_out_date'),
            'nights': request.data.get('nights', 1),
            'total_price': request.data.get('total_price', 0),
            'message': request.data.get('message', ''),
            'status': request.data.get('status', 'requested'),
        }
        
        booking = Booking.objects.create(**booking_data)
        
        # Create conversation for this booking
        try:
            # Get admin users
            admin_users = User.objects.filter(
                Q(is_superuser=True) | Q(is_staff=True) | 
                Q(email__in=['admin@ereft.com', 'melaku.garsamo@gmail.com', 'cb.garsamo@gmail.com', 'lydiageleta45@gmail.com'])
            ).first()
            
            if admin_users:
                conversation = Conversation.objects.create(booking=booking)
                conversation.participants.add(request.user, admin_users)
                
                # Create initial system message
                Message.objects.create(
                    conversation=conversation,
                    sender=request.user,
                    recipient=admin_users,
                    content=f"New booking request submitted for {property_obj.title}. Check-in: {booking.check_in_date}, Check-out: {booking.check_out_date}."
                )
        except Exception as e:
            # If conversation creation fails, booking still succeeds
            print(f"Error creating conversation: {e}")
        
        serializer = BookingSerializer(booking, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_bookings(request):
    """Get current user's bookings"""
    bookings = Booking.objects.filter(guest=request.user).order_by('-created_at')
    serializer = BookingSerializer(bookings, many=True, context={'request': request})
    return Response({
        'results': serializer.data,
        'count': len(serializer.data)
    })


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def booking_detail(request, booking_id):
    """
    GET: Get booking details
    PATCH: Update booking status (admin only for status changes)
    """
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check permissions
    if not is_admin(request.user) and booking.guest != request.user:
        return Response({'detail': 'You do not have permission to view this booking'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        serializer = BookingSerializer(booking, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'PATCH':
        # Only admins can change status
        if not is_admin(request.user):
            return Response({'detail': 'Only admins can update booking status'}, status=status.HTTP_403_FORBIDDEN)
        
        new_status = request.data.get('status')
        if new_status:
            booking.status = new_status
            if new_status == 'approved':
                booking.confirmed_at = timezone.now()
            elif new_status == 'cancelled':
                booking.cancelled_at = timezone.now()
            booking.save()
        
        # If message provided, send it
        message_content = request.data.get('message')
        if message_content:
            # Find or create conversation
            conversation = booking.conversations.first()
            if not conversation:
                admin_users = User.objects.filter(
                    Q(is_superuser=True) | Q(is_staff=True) | 
                    Q(email__in=['admin@ereft.com', 'melaku.garsamo@gmail.com', 'cb.garsamo@gmail.com', 'lydiageleta45@gmail.com'])
                ).first()
                if admin_users and booking.guest:
                    conversation = Conversation.objects.create(booking=booking)
                    conversation.participants.add(request.user, booking.guest)
            
            if conversation and booking.guest:
                Message.objects.create(
                    conversation=conversation,
                    sender=request.user,
                    recipient=booking.guest,
                    content=message_content
                )
        
        serializer = BookingSerializer(booking, context={'request': request})
        return Response(serializer.data)
