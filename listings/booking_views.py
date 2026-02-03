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
        try:
            serializer = BookingSerializer(bookings, many=True, context={'request': request})
            return Response({
                'results': serializer.data,
                'count': len(serializer.data)
            })
        except Exception as e:
            print(f"Error serializing bookings: {e}")
            import traceback
            traceback.print_exc()
            return Response({
                'detail': 'Error loading bookings. Please try again later.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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
        
        # Parse dates and calculate if needed
        from datetime import datetime, date
        check_in_date_obj = None
        check_out_date_obj = None
        
        if check_in:
            try:
                # Try YYYY-MM-DD format first (standard HTML date input)
                check_in_date_obj = datetime.strptime(check_in, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                try:
                    # Try other common formats
                    check_in_date_obj = datetime.strptime(check_in, '%Y/%m/%d').date()
                except (ValueError, TypeError):
                    try:
                        check_in_date_obj = datetime.strptime(check_in, '%m/%d/%Y').date()
                    except (ValueError, TypeError):
                        print(f"Warning: Could not parse check_in_date: {check_in}")
        
        if check_out:
            try:
                check_out_date_obj = datetime.strptime(check_out, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                try:
                    check_out_date_obj = datetime.strptime(check_out, '%Y/%m/%d').date()
                except (ValueError, TypeError):
                    try:
                        check_out_date_obj = datetime.strptime(check_out, '%m/%d/%Y').date()
                    except (ValueError, TypeError):
                        print(f"Warning: Could not parse check_out_date: {check_out}")
        
        # Validate that dates were successfully parsed
        if not check_in_date_obj or not check_out_date_obj:
            return Response({'detail': 'Invalid date format. Please use YYYY-MM-DD format for dates.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Use parsed dates for calculations
        calculated_nights = (check_out_date_obj - check_in_date_obj).days
        if calculated_nights <= 0:
            return Response({'detail': 'Check-out date must be after check-in date'}, status=status.HTTP_400_BAD_REQUEST)
        
        if calculated_nights > 0:
            nights = calculated_nights
            if not total_price and property_obj.price:
                total_price = calculated_nights * float(property_obj.price)
        
        # Validate dates are in the future and check-out is after check-in
        # CRITICAL: Use date objects for validation, not strings
        today = date.today()
        if check_in_date_obj < today:
            return Response({'detail': 'Check-in date cannot be in the past'}, status=status.HTTP_400_BAD_REQUEST)
        if check_out_date_obj <= check_in_date_obj:
            return Response({'detail': 'Check-out date must be after check-in date'}, status=status.HTTP_400_BAD_REQUEST)
        
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
        
        # Validate all required fields before creating booking
        if not guest_email:
            return Response({'detail': 'Guest email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create booking with all auto-populated data
        # Ensure all fields meet database constraints
        try:
            # Ensure guest_phone doesn't exceed max_length (50)
            guest_phone_clean = (guest_phone or '')[:50]
            
            # Ensure guest_name doesn't exceed max_length (255)
            guest_name_clean = (guest_name or 'Guest')[:255]
            
            # Ensure total_price is a Decimal
            from decimal import Decimal
            total_price_decimal = Decimal(str(total_price or 0))
            
            # Ensure nights is a positive integer
            nights_int = max(1, int(nights or 1))
            
            # CRITICAL: Use date objects directly - Django ORM will handle conversion
            booking_data = {
                'property': property_obj,
                'guest': request.user if request.user.is_authenticated else None,
                'guest_name': guest_name_clean,
                'guest_email': guest_email,
                'guest_phone': guest_phone_clean,
                'check_in_date': check_in_date_obj,  # Use date object, not string
                'check_out_date': check_out_date_obj,  # Use date object, not string
                'nights': nights_int,
                'total_price': total_price_decimal,
                'message': (request.data.get('message', '') or '')[:5000],  # Limit message length
                'status': request.data.get('status', 'requested'),
            }
            
            booking = Booking.objects.create(**booking_data)
            print(f"✅ Booking created successfully: {booking.id}")
        except Exception as e:
            print(f"❌ Error creating booking: {e}")
            import traceback
            traceback.print_exc()
            return Response({'detail': f'Failed to create booking: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Create booking thread conversation (CRITICAL: This is the unified booking thread)
        # This MUST succeed for the booking system to work properly
        conversation_created = False
        try:
            # Get admin users - try multiple methods to ensure we find one
            admin_users = None
            admin_emails = ['admin@ereft.com', 'melaku.garsamo@gmail.com', 'cb.garsamo@gmail.com', 'lydiageleta45@gmail.com']
            
            # Try to find admin by email first
            for email in admin_emails:
                try:
                    admin_user = User.objects.filter(email__iexact=email).first()
                    if admin_user:
                        admin_users = admin_user
                        break
                except Exception:
                    continue
            
            # Fallback to superuser or staff
            if not admin_users:
                admin_users = User.objects.filter(
                    Q(is_superuser=True) | Q(is_staff=True)
                ).first()
            
            if admin_users and request.user.is_authenticated:
                # Check if conversation already exists for this booking
                existing_conversation = Conversation.objects.filter(booking=booking).first()
                if existing_conversation:
                    conversation = existing_conversation
                    print(f"✅ Using existing conversation: {conversation.id}")
                else:
                    # Create the booking thread conversation
                    conversation = Conversation.objects.create(booking=booking)
                    conversation.participants.add(request.user, admin_users)
                    print(f"✅ Created new conversation: {conversation.id}")
                conversation_created = True
                
                # Create initial system message with property details
                try:
                    # Get property URL - handle both http and https
                    scheme = request.scheme if hasattr(request, 'scheme') else 'https'
                    host = request.get_host() if hasattr(request, 'get_host') else 'www.ereft.com'
                    property_url = f"{scheme}://{host}/properties/{property_obj.id}"
                except Exception:
                    property_url = f"https://www.ereft.com/properties/{property_obj.id}"
                
                # Get property image with fallbacks
                property_image = ""
                try:
                    if hasattr(property_obj, 'images') and property_obj.images.exists():
                        primary_img = property_obj.images.filter(is_primary=True).first()
                        if primary_img:
                            property_image = primary_img.image_url or ""
                        else:
                            first_img = property_obj.images.first()
                            if first_img:
                                property_image = first_img.image_url or ""
                except Exception:
                    pass
                
                # Build comprehensive initial message
                initial_message = f"New booking request submitted for {property_obj.title or 'Property'}.\n\n"
                initial_message += f"Property: {property_obj.title or 'Property'}\n"
                initial_message += f"Property ID: {property_obj.id}\n"
                initial_message += f"Location: {property_obj.city or 'Unknown'}" + (f", {property_obj.sub_city}" if property_obj.sub_city else "") + "\n"
                initial_message += f"Check-in: {booking.check_in_date}\n"
                initial_message += f"Check-out: {booking.check_out_date}\n"
                initial_message += f"Nights: {booking.nights or 1}\n"
                initial_message += f"Total Price: {booking.total_price or 0} ETB\n"
                initial_message += f"\nProperty Link: {property_url}\n"
                if property_image:
                    initial_message += f"Property Image: {property_image}\n"
                initial_message += f"\nGuest Information:\n"
                initial_message += f"Name: {booking.guest_name or 'Guest'}\n"
                initial_message += f"Email: {booking.guest_email or 'Not provided'}\n"
                if booking.guest_phone:
                    initial_message += f"Phone: {booking.guest_phone}\n"
                if booking.message:
                    initial_message += f"\nGuest Message: {booking.message}"
                
                # Create the initial message in the booking thread
                Message.objects.create(
                    conversation=conversation,
                    sender=request.user,
                    recipient=admin_users,
                    content=initial_message
                )
            else:
                print(f"Warning: Could not create booking thread - admin_users={admin_users}, user_authenticated={request.user.is_authenticated}")
        except Exception as e:
            # Log the error but don't fail the booking
            import traceback
            print(f"Error creating booking thread: {e}")
            traceback.print_exc()
            # Booking still succeeds even if thread creation fails
        
        serializer = BookingSerializer(booking, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_bookings(request):
    """Get current user's bookings"""
    try:
        bookings = Booking.objects.filter(guest=request.user).order_by('-created_at')
        serializer = BookingSerializer(bookings, many=True, context={'request': request})
        return Response({
            'results': serializer.data,
            'count': len(serializer.data)
        })
    except Exception as e:
        print(f"Error fetching user bookings: {e}")
        import traceback
        traceback.print_exc()
        return Response({
            'detail': 'Error loading your bookings. Please try again later.',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
