# FILE: ereft_api/listings/utils.py
# PRODUCTION READY: All utility functions properly configured per .cursorrules
# TIMESTAMP: 2025-01-15 16:30:00 - FORCE REDEPLOYMENT
# 🚨 CRITICAL: Utility functions optimized for production deployment

import os
import json
import requests
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.db import models
from .models import Property, User, UserProfile

import uuid
from django.utils.html import strip_tags
# from PIL import Image  # Disabled - causes build failures on Render per .cursorrules
# from io import BytesIO
# from django.core.files import File
import cloudinary
import cloudinary.uploader
import cloudinary.api

def send_property_inquiry_email(contact):
    """
    Send email notification for property inquiry
    """
    subject = f'New Property Inquiry: {contact.property.title}'
    
    # HTML content
    html_message = render_to_string('emails/property_inquiry.html', {
        'contact': contact,
        'property': contact.property,
    })
    
    # Plain text content
    plain_message = strip_tags(html_message)
    
    # Send to property owner
    if contact.property.owner.email:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[contact.property.owner.email],
            html_message=html_message,
            fail_silently=False,
        )
    
    # Send to agent if different from owner
    if contact.property.agent and contact.property.agent.email != contact.property.owner.email:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[contact.property.agent.email],
            html_message=html_message,
            fail_silently=False,
        )

def send_welcome_email(user):
    """
    Send welcome email to new users
    """
    subject = 'Welcome to Ereft - Your Real Estate Platform'
    
    html_message = render_to_string('emails/welcome.html', {
        'user': user,
    })
    
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )

def compress_image(image_field, max_size=(800, 600), quality=85):
    """
    Compress image before saving - DISABLED per .cursorrules (Pillow causes build failures)
    """
    # PIL/Pillow disabled for Render deployment
    print("⚠️ compress_image disabled - using Cloudinary transformations instead")
    return image_field

def generate_property_slug(title, property_id):
    """
    Generate URL-friendly slug for property
    """
    import re
    from django.utils.text import slugify
    
    # Create base slug from title
    base_slug = slugify(title)
    
    # Add property ID for uniqueness
    slug = f"{base_slug}-{property_id}"
    
    return slug

def calculate_price_per_sqft(price, square_feet):
    """
    Calculate price per square foot
    """
    if square_feet and square_feet > 0:
        return price / square_feet
    return None

def format_currency(amount, currency='ETB'):
    """
    Format currency for display
    """
    if currency == 'ETB':
        return f"ETB {amount:,.2f}"
    return f"{currency} {amount:,.2f}"

def get_property_stats():
    """
    Get basic property statistics
    """
    from django.db import models
    from .models import Property
    
    total_properties = Property.objects.filter(is_active=True).count()
    for_sale = Property.objects.filter(is_active=True, listing_type='sale').count()
    for_rent = Property.objects.filter(is_active=True, listing_type='rent').count()
    
    # Calculate average price
    avg_price = Property.objects.filter(
        is_active=True, 
        listing_type='sale'
    ).aggregate(avg_price=models.Avg('price'))['avg_price'] or 0
    
    return {
        'total_properties': total_properties,
        'for_sale': for_sale,
        'for_rent': for_rent,
        'average_price': avg_price
    }

def validate_phone_number(phone):
    """
    Validate Ethiopian phone number format
    """
    import re
    
    # Ethiopian phone number patterns
    patterns = [
        r'^\+251[0-9]{9}$',  # +251XXXXXXXXX
        r'^251[0-9]{9}$',    # 251XXXXXXXXX
        r'^0[0-9]{9}$',      # 0XXXXXXXXX
        r'^[0-9]{9}$',       # XXXXXXXXX
    ]
    
    for pattern in patterns:
        if re.match(pattern, phone):
            return True
    
    return False

def format_phone_number(phone):
    """
    Format phone number to standard Ethiopian format
    """
    import re
    
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Handle different formats
    if len(digits) == 9:
        return f"+251{digits}"
    elif len(digits) == 10 and digits.startswith('0'):
        return f"+251{digits[1:]}"
    elif len(digits) == 12 and digits.startswith('251'):
        return f"+{digits}"
    elif len(digits) == 13 and digits.startswith('251'):
        return f"+{digits}"
    
    return phone

def upload_image_to_cloudinary(image_file, folder="ereft_properties"):
    """
    Upload an image to Cloudinary and return the public URL
    
    Args:
        image_file: The image file to upload
        folder: The folder in Cloudinary to store the image
    
    Returns:
        dict: Cloudinary upload result with public_id, url, etc.
    """
    try:
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            image_file,
            folder=folder,
            resource_type="image",
            transformation=[
                {"width": 1200, "height": 800, "crop": "limit"},
                {"quality": "auto:good", "fetch_format": "auto"}
            ]
        )
        
        print(f"✅ Image uploaded successfully to Cloudinary: {result['public_id']}")
        return result
        
    except Exception as e:
        print(f"❌ Error uploading image to Cloudinary: {str(e)}")
        raise e

def delete_image_from_cloudinary(public_id):
    """
    Delete an image from Cloudinary
    
    Args:
        public_id: The public ID of the image to delete
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        result = cloudinary.uploader.destroy(public_id)
        print(f"✅ Image deleted from Cloudinary: {public_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error deleting image from Cloudinary: {str(e)}")
        return False

def get_cloudinary_url(public_id, transformation=None):
    """
    Get a Cloudinary URL with optional transformations
    
    Args:
        public_id: The public ID of the image
        transformation: Optional transformation parameters
    
    Returns:
        str: The Cloudinary URL
    """
    try:
        if transformation:
            url = cloudinary.CloudinaryImage(public_id).build_url(**transformation)
        else:
            url = cloudinary.CloudinaryImage(public_id).build_url()
        
        return url
        
    except Exception as e:
        print(f"❌ Error generating Cloudinary URL: {str(e)}")
        return None

def optimize_image_for_property(image_file):
    """
    Optimize an image specifically for property listings
    
    Args:
        image_file: The image file to optimize
    
    Returns:
        dict: Cloudinary upload result
    """
    try:
        result = cloudinary.uploader.upload(
            image_file,
            folder="ereft_properties",
            resource_type="image",
            transformation=[
                {"width": 1200, "height": 800, "crop": "limit"},
                {"quality": "auto:good", "fetch_format": "auto"},
                {"effect": "auto_contrast"},
                {"effect": "auto_brightness"}
            ]
        )
        
        print(f"✅ Property image optimized and uploaded: {result['public_id']}")
        return result
        
    except Exception as e:
        print(f"❌ Error optimizing property image: {str(e)}")
        raise e

def handle_property_image_upload(image_file, property_id):
    """
    Handle property image upload to Cloudinary and return image data
    
    Args:
        image_file: The uploaded image file
        property_id: The property ID for organization
    
    Returns:
        dict: Image data with Cloudinary URL and metadata
    """
    try:
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            image_file,
            folder=f"ereft_properties/{property_id}",
            resource_type="image",
            transformation=[
                {"width": 1200, "height": 800, "crop": "limit"},
                {"quality": "auto:good", "fetch_format": "auto"}
            ]
        )
        
        # Return formatted image data
        return {
            'public_id': result['public_id'],
            'url': result['secure_url'],
            'width': result['width'],
            'height': result['height'],
            'format': result['format'],
            'size': result['bytes']
        }
        
    except Exception as e:
        print(f"❌ Error handling property image upload: {str(e)}")
        raise e

def send_verification_email(user, request):
    """
    Send real verification email to user
    """
    try:
        # Generate verification token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Create verification URL
        verification_url = request.build_absolute_uri(
            reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
        )
        
        # Email content
        subject = 'Verify Your Ereft Account'
        message = f"""
        Hello {user.first_name or user.username},
        
        Welcome to Ereft! Please verify your email address by clicking the link below:
        
        {verification_url}
        
        If you didn't create this account, please ignore this email.
        
        Best regards,
        The Ereft Team
        """
        
        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        return True
    except Exception as e:
        print(f"🔐 Failed to send verification email: {e}")
        return False

def send_password_reset_email(user, request):
    """
    Send real password reset email to user
    """
    try:
        # Generate password reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Create reset URL
        reset_url = request.build_absolute_uri(
            reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        )
        
        # Email content
        subject = 'Reset Your Ereft Password'
        message = f"""
        Hello {user.first_name or user.username},
        
        You requested a password reset for your Ereft account. Click the link below to reset your password:
        
        {reset_url}
        
        If you didn't request this reset, please ignore this email.
        
        This link will expire in 24 hours.
        
        Best regards,
        The Ereft Team
        """
        
        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        return True
    except Exception as e:
        print(f"🔐 Failed to send password reset email: {e}")
        return False

def verify_email_token(uidb64, token):
    """
    Verify email verification token
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        
        if default_token_generator.check_token(user, token):
            # Update user profile
            try:
                profile = UserProfile.objects.get(user=user)
                profile.email_verified = True
                profile.save()
            except UserProfile.DoesNotExist:
                UserProfile.objects.create(
                    user=user,
                    email_verified=True,
                    phone_verified=False
                )
            return user
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        pass
    return None

def reset_password_with_token(uidb64, token, new_password):
    """
    Reset password using token
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        
        if default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return user
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        pass
    return None
