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
from .models import Property, Booking, Conversation, Message, Availability
from .serializers import BookingSerializer, ConversationSerializer, MessageSerializer
from django.utils import timezone
from datetime import timedelta


def is_admin(user):
    """Check if user is admin"""
    if not user.is_authenticated:
        return False
    admin_emails = ['admin@ereft.com', 'melaku.garsamo@gmail.com', 'cb.garsamo@gmail.com', 'lydiageleta45@gmail.com']
    return user.is_superuser or user.is_staff or (user.email and user.email.lower() in admin_emails)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def bookings_list_create(request):
    """
    GET: List all bookings (admin only) or filtered by status
    POST: Create a new booking request
    """
    if request.method == 'GET':
        # Only admins can list all bookings
        if not is_admin(request.user):
            return Response({'detail': 'You do not have permission to view all bookings'}, status=status.HTTP_403_FORBIDDEN)
        
        status_filter = request.query_params.get('status')
        bookings = Booking.objects.all()
        
        if status_filter:
            bookings = bookings.filter(status=status_filter)
        
        bookings = bookings.order_by('-created_at')
        serializer = BookingSerializer(bookings, many=True, context={'request': request})
        return Response({
            'results': serializer.data,
            'count': len(serializer.data)
        })
    
    elif request.method == 'POST':
        # Create new booking request with automatic data population
        property_id = request.data.get('property')
        
        # Auto-populate property ID if missing (try to get from URL or use fallback)
        if not property_id:
            # Try to extract from referer URL or use a default
            referer = request.META.get('HTTP_REFERER', '')
            import re
            property_match = re.search(r'/properties/([a-f0-9-]+)', referer)
            if property_match:
                property_id = property_match.group(1)
            else:
                # Last resort: try to get from message if it contains property link
                message = request.data.get('message', '')
                property_match = re.search(r'/properties/([a-f0-9-]+)', message)
                if property_match:
                    property_id = property_match.group(1)
        
        if not property_id:
            return Response({'detail': 'Property ID is required. Please ensure you are booking from a property page.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            property_obj = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return Response({'detail': 'Property not found. The property may have been removed.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Auto-calculate nights and total price if missing
        check_in = request.data.get('check_in_date')
        check_out = request.data.get('check_out_date')
        nights = request.data.get('nights')
        total_price = request.data.get('total_price')
        
        if check_in and check_out and (not nights or not total_price):
            from datetime import datetime
            try:
                check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
                check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
                calculated_nights = (check_out_date - check_in_date).days
                if calculated_nights > 0:
                    nights = calculated_nights
                    if not total_price and property_obj.price:
                        total_price = calculated_nights * float(property_obj.price)
            except (ValueError, TypeError):
                pass
        
        # Auto-populate user info if missing
        guest_name = request.data.get('guest_name')
        guest_email = request.data.get('guest_email')
        guest_phone = request.data.get('guest_phone', '')
        
        if not guest_name and request.user.is_authenticated:
            guest_name = request.user.get_full_name() or request.user.username or 'Guest'
        if not guest_email and request.user.is_authenticated:
            guest_email = request.user.email or ''
        if not guest_name:
            guest_name = 'Guest'
        if not guest_email:
            guest_email = request.data.get('email', '')
        
        # Create booking with all auto-populated data
        booking_data = {
            'property': property_obj,
            'guest': request.user if request.user.is_authenticated else None,
            'guest_name': guest_name,
            'guest_email': guest_email,
            'guest_phone': guest_phone,
            'check_in_date': check_in,
            'check_out_date': check_out,
            'nights': nights or 1,
            'total_price': total_price or 0,
            'message': request.data.get('message', ''),
            'status': request.data.get('status', 'requested'),
        }
        
        booking = Booking.objects.create(**booking_data)
        
        # Create booking thread conversation (CRITICAL: This is the unified booking thread)
        try:
            # Get admin users
            admin_users = User.objects.filter(
                Q(is_superuser=True) | Q(is_staff=True) | 
                Q(email__in=['admin@ereft.com', 'melaku.garsamo@gmail.com', 'cb.garsamo@gmail.com', 'lydiageleta45@gmail.com'])
            ).first()
            
            if admin_users and request.user.is_authenticated:
                # Create the booking thread conversation
                conversation = Conversation.objects.create(booking=booking)
                conversation.participants.add(request.user, admin_users)
                
                # Create initial system message with property details
                property_url = f"{request.scheme}://{request.get_host()}/properties/{property_obj.id}"
                property_image = ""
                if property_obj.images.exists():
                    primary_img = property_obj.images.filter(is_primary=True).first()
                    if primary_img:
                        property_image = primary_img.image_url or ""
                    else:
                        property_image = property_obj.images.first().image_url or ""
                
                initial_message = f"New booking request submitted for {property_obj.title}.\n\n"
                initial_message += f"Property: {property_obj.title}\n"
                initial_message += f"Location: {property_obj.city}" + (f", {property_obj.sub_city}" if property_obj.sub_city else "") + "\n"
                initial_message += f"Check-in: {booking.check_in_date}\n"
                initial_message += f"Check-out: {booking.check_out_date}\n"
                initial_message += f"Nights: {booking.nights}\n"
                initial_message += f"Total Price: {booking.total_price} ETB\n"
                if property_url:
                    initial_message += f"\nProperty Link: {property_url}\n"
                if booking.message:
                    initial_message += f"\nGuest Message: {booking.message}"
                
                Message.objects.create(
                    conversation=conversation,
                    sender=request.user,
                    recipient=admin_users,
                    content=initial_message
                )
        except Exception as e:
            # If conversation creation fails, booking still succeeds
            print(f"Error creating booking thread: {e}")
        
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
        old_status = booking.status
        
        if new_status:
            booking.status = new_status
            if new_status == 'confirmed' or new_status == 'approved':
                booking.confirmed_at = timezone.now()
            elif new_status == 'cancelled':
                booking.cancelled_at = timezone.now()
            booking.save()
            
            # Lock property dates when booking is confirmed
            if new_status == 'confirmed' and old_status != 'confirmed':
                current_date = booking.check_in_date
                while current_date < booking.check_out_date:
                    Availability.objects.update_or_create(
                        property=booking.property,
                        date=current_date,
                        defaults={
                            'status': 'booked',
                            'notes': f'Booked by {booking.guest_name} (Booking ID: {booking.id})'
                        }
                    )
                    current_date += timedelta(days=1)
            
            # Update conversation updated_at when status changes
            conversation = booking.conversations.first()
            if conversation:
                conversation.updated_at = timezone.now()
                conversation.save()
                
                # Create status update message in the booking thread
                status_messages = {
                    'pending_payment': 'Booking status updated to Pending Payment. Please complete payment to proceed.',
                    'confirmed': 'Booking confirmed! Your booking is now confirmed. The property has been locked for your selected dates.',
                    'approved': 'Booking approved! Your booking has been approved.',
                    'rejected': 'Booking request has been rejected.',
                    'cancelled': 'Booking has been cancelled.',
                }
                
                if new_status in status_messages and booking.guest:
                    status_message = f"Status Update: {status_messages[new_status]}"
                    Message.objects.create(
                        conversation=conversation,
                        sender=request.user,
                        recipient=booking.guest,
                        content=status_message
                    )
        
        # If message provided, send it in the booking thread
        message_content = request.data.get('message')
        if message_content:
            # Find or create conversation (should always exist for bookings)
            conversation = booking.conversations.first()
            if not conversation:
                # Fallback: create conversation if it doesn't exist
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
