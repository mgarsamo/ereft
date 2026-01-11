"""
Availability and Booking Management API Views for Vacation Homes
"""
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta, date, datetime
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from .models import Property, Availability, Booking, RecurringAvailabilityRule
from .serializers import AvailabilitySerializer, BookingSerializer, RecurringAvailabilityRuleSerializer

def is_property_owner_or_admin(user, property_obj):
    """Check if user owns the property or is an admin"""
    if not user.is_authenticated:
        return False
    
    # Check if admin
    admin_emails = ['admin@ereft.com', 'melaku.garsamo@gmail.com', 'cb.garsamo@gmail.com', 'lydiageleta45@gmail.com']
    if user.is_superuser or user.is_staff or (user.email and user.email.lower() in [e.lower() for e in admin_emails]):
        return True
    
    # Check if owner
    return property_obj.owner == user

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def property_availability(request, property_id):
    """
    GET: List all availability dates for a property
    POST: Bulk create/update availability dates
    """
    property_obj = get_object_or_404(Property, id=property_id)
    
    # Only property owner or admin can manage availability
    if not is_property_owner_or_admin(request.user, property_obj):
        return Response(
            {'detail': 'You do not have permission to manage this property\'s availability.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if request.method == 'GET':
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = Availability.objects.filter(property=property_obj)
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        serializer = AvailabilitySerializer(queryset.order_by('date'), many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Bulk create/update availability dates
        dates_data = request.data.get('dates', [])
        if not isinstance(dates_data, list):
            return Response(
                {'detail': 'dates must be a list of date objects'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_count = 0
        updated_count = 0
        errors = []
        
        for date_data in dates_data:
            date_value = date_data.get('date')
            status_value = date_data.get('status', 'available')
            notes = date_data.get('notes', '')
            
            if not date_value:
                errors.append({'detail': 'date is required for each availability entry'})
                continue
            
            try:
                # Try to parse date if it's a string
                if isinstance(date_value, str):
                    date_obj = datetime.strptime(date_value, '%Y-%m-%d').date()
                else:
                    date_obj = date_value
                
                availability, created = Availability.objects.update_or_create(
                    property=property_obj,
                    date=date_obj,
                    defaults={
                        'status': status_value,
                        'notes': notes
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
                    
            except ValueError as e:
                errors.append({'date': date_value, 'error': f'Invalid date format: {str(e)}'})
            except Exception as e:
                errors.append({'date': date_value, 'error': str(e)})
        
        return Response({
            'created': created_count,
            'updated': updated_count,
            'errors': errors if errors else None
        }, status=status.HTTP_201_CREATED if created_count > 0 else status.HTTP_200_OK)

@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def availability_detail(request, property_id, date_str):
    """
    Update or delete a specific availability date
    """
    property_obj = get_object_or_404(Property, id=property_id)
    
    # Only property owner or admin can manage availability
    if not is_property_owner_or_admin(request.user, property_obj):
        return Response(
            {'detail': 'You do not have permission to manage this property\'s availability.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return Response(
            {'detail': 'Invalid date format. Use YYYY-MM-DD'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    availability = get_object_or_404(Availability, property=property_obj, date=date_obj)
    
    if request.method == 'PUT':
        serializer = AvailabilitySerializer(availability, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        availability.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def property_bookings(request, property_id):
    """
    GET: List all bookings for a property (owner/admin only)
    POST: Create a booking request for a vacation home
    """
    property_obj = get_object_or_404(Property, id=property_id)
    
    if request.method == 'GET':
        # Only property owner or admin can view bookings
        if not is_property_owner_or_admin(request.user, property_obj):
            return Response(
                {'detail': 'You do not have permission to view bookings for this property.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        bookings = Booking.objects.filter(property=property_obj).order_by('-created_at')
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Anyone can create a booking request (but must check availability)
        check_in_date = request.data.get('check_in_date')
        check_out_date = request.data.get('check_out_date')
        guest_name = request.data.get('guest_name', '')
        guest_email = request.data.get('guest_email', '')
        guest_phone = request.data.get('guest_phone', '')
        message = request.data.get('message', '')
        
        if not all([check_in_date, check_out_date, guest_name, guest_email, guest_phone]):
            return Response(
                {'detail': 'check_in_date, check_out_date, guest_name, guest_email, and guest_phone are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            check_in = datetime.strptime(check_in_date, '%Y-%m-%d').date()
            check_out = datetime.strptime(check_out_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'detail': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if check_out <= check_in:
            return Response(
                {'detail': 'check_out_date must be after check_in_date'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if dates are available
        nights = (check_out - check_in).days
        current_date = check_in
        unavailable_dates = []
        
        while current_date < check_out:
            availability = Availability.objects.filter(
                property=property_obj,
                date=current_date
            ).first()
            
            if not availability or availability.status != 'available':
                unavailable_dates.append(str(current_date))
            
            current_date += timedelta(days=1)
        
        if unavailable_dates:
            return Response(
                {'detail': f'Property is not available for the selected dates: {", ".join(unavailable_dates)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate total price
        price_per_night = property_obj.price
        total_price = price_per_night * nights
        
        # Determine if instant booking
        is_instant = property_obj.booking_preference == 'instant'
        booking_status = 'confirmed' if is_instant else 'pending'
        
        # Create booking (Booking.save() will automatically create availability entries if status is 'confirmed')
        booking = Booking.objects.create(
            property=property_obj,
            guest=request.user if request.user.is_authenticated else None,
            guest_name=guest_name,
            guest_email=guest_email,
            guest_phone=guest_phone,
            check_in_date=check_in,
            check_out_date=check_out,
            nights=nights,
            total_price=total_price,
            message=message,
            status=booking_status,
            is_instant_booking=is_instant
        )
        
        # If instant booking, mark dates as booked immediately
        if booking_status == 'confirmed':
            booking.confirmed_at = timezone.now()
            booking.save()  # This will trigger the save() method which creates availability entries
        
        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def booking_status(request, booking_id):
    """
    Update booking status (confirm, cancel, etc.) - owner/admin only
    """
    booking = get_object_or_404(Booking, id=booking_id)
    property_obj = booking.property
    
    # Only property owner or admin can update booking status
    if not is_property_owner_or_admin(request.user, property_obj):
        return Response(
            {'detail': 'You do not have permission to update this booking.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    new_status = request.data.get('status')
    if new_status not in ['pending', 'confirmed', 'cancelled', 'completed']:
        return Response(
            {'detail': 'Invalid status. Must be one of: pending, confirmed, cancelled, completed'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    booking.status = new_status
    
    if new_status == 'confirmed':
        booking.confirmed_at = timezone.now()
        booking.cancelled_at = None
    elif new_status == 'cancelled':
        booking.cancelled_at = timezone.now()
        booking.confirmed_at = None
    
    booking.save()
    
    serializer = BookingSerializer(booking)
    return Response(serializer.data)
