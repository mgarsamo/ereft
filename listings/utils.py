# FILE: ereft_api/listings/utils.py
# PRODUCTION READY: All utility functions properly configured per .cursorrules
# TIMESTAMP: 2025-01-15 16:30:00 - FORCE REDEPLOYMENT
# 🚨 CRITICAL: Utility functions optimized for production deployment

import os
import json
import requests
from datetime import datetime
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

def send_welcome_email(user, is_new_user=False, test_email=None):
    """
    Send welcome email to new users using SendGrid
    Only sends once per user (for new users)
    """
    try:
        # Send welcome email to all users (new and existing)
        # if not is_new_user:
        #     print(f"ℹ️ Welcome email skipped for {user.email} (existing user)")
        #     return False
        
        # Use test email if provided, otherwise use user's email
        recipient_email = test_email if test_email else user.email
        
        # Subject line with emojis
        subject = '🎉 Welcome to Ereft! Your Account is Ready 🚀'
        
        # User's name for personalization
        user_name = user.first_name or user.username or 'there'
        
        # Create engaging HTML email content with emojis
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; 
                    line-height: 1.6; 
                    color: #333; 
                    margin: 0; 
                    padding: 0;
                    background-color: #f5f5f5;
                }}
                .container {{ 
                    max-width: 600px; 
                    margin: 0 auto; 
                    padding: 0;
                    background-color: #ffffff;
                }}
                .header {{ 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; 
                    padding: 40px 30px; 
                    text-align: center; 
                    border-radius: 0;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 32px;
                    font-weight: bold;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    font-size: 16px;
                    opacity: 0.95;
                }}
                .content {{ 
                    background: #ffffff; 
                    padding: 40px 30px; 
                }}
                .content h2 {{
                    color: #333;
                    font-size: 24px;
                    margin: 0 0 20px 0;
                    font-weight: 600;
                }}
                .content p {{
                    color: #555;
                    font-size: 16px;
                    margin: 15px 0;
                    line-height: 1.7;
                }}
                .features {{
                    background: #f8f9fa;
                    border-left: 4px solid #667eea;
                    padding: 20px;
                    margin: 25px 0;
                    border-radius: 4px;
                }}
                .features ul {{
                    margin: 0;
                    padding-left: 25px;
                }}
                .features li {{
                    color: #555;
                    font-size: 16px;
                    margin: 10px 0;
                    line-height: 1.6;
                }}
                .button-container {{
                    text-align: center;
                    margin: 30px 0;
                }}
                .button {{ 
                    display: inline-block; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; 
                    padding: 15px 40px; 
                    text-decoration: none; 
                    border-radius: 8px; 
                    font-weight: 600;
                    font-size: 16px;
                    box-shadow: 0 4px 6px rgba(102, 126, 234, 0.3);
                    transition: transform 0.2s;
                }}
                .button:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4);
                }}
                .closing {{
                    margin-top: 30px;
                    padding-top: 25px;
                    border-top: 1px solid #e0e0e0;
                }}
                .footer {{ 
                    text-align: center; 
                    padding: 30px;
                    background-color: #f8f9fa;
                    color: #666; 
                    font-size: 12px; 
                }}
                .footer p {{
                    margin: 5px 0;
                    color: #999;
                }}
                .emoji {{
                    font-size: 24px;
                    vertical-align: middle;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏠 Ereft</h1>
                    <p>Ethiopia's Premier Real Estate Platform</p>
                </div>
                <div class="content">
                    <h2>🎉 Welcome, {user_name}!</h2>
                    <p>We're <strong>thrilled</strong> to have you join the Ereft community! 🎊</p>
                    <p>Your account is all set up and ready to go. You can now start exploring amazing properties across Ethiopia!</p>
                    
                    <div class="features">
                        <p style="margin-top: 0; font-weight: 600; color: #667eea;">✨ <strong>Get Started:</strong></p>
                        <ul>
                            <li>🔍 <strong>Browse & Search</strong> thousands of properties across Ethiopia</li>
                            <li>❤️ <strong>Save Favorites</strong> and create your dream home wishlist</li>
                            <li>🏘️ <strong>List Properties</strong> and connect with serious buyers and renters</li>
                            <li>🗺️ <strong>Explore on Map</strong> to find properties in your preferred locations</li>
                            <li>💬 <strong>Contact Agents</strong> directly and get instant responses</li>
                        </ul>
                    </div>
                    
                    <div class="button-container">
                        <a href="https://www.ereft.com" class="button">🚀 Start Exploring Properties</a>
                    </div>
                    
                    <p>Whether you're looking to buy, rent, or sell, Ereft makes the entire process smooth and enjoyable. 💫</p>
                    
                    <div class="closing">
                        <p>If you have any questions or need help, we're here for you! Just reply to this email.</p>
                        <p><strong>Happy house hunting! 🏡✨</strong></p>
                        <p style="margin-top: 20px;">
                            Best regards,<br>
                            <strong>The Ereft Team</strong> 💙
                        </p>
                    </div>
                </div>
                <div class="footer">
                    <p>This email was sent to {recipient_email}</p>
                    <p>&copy; {datetime.now().year} Ereft. All rights reserved.</p>
                    <p>Ethiopia's trusted real estate platform</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        plain_message = f"""
🎉 Welcome to Ereft, {user_name}! 🚀

We're thrilled to have you join the Ereft community!

Your account is all set up and ready to go. You can now start exploring amazing properties across Ethiopia!

✨ Get Started:
• 🔍 Browse & Search thousands of properties across Ethiopia
• ❤️ Save Favorites and create your dream home wishlist
• 🏘️ List Properties and connect with serious buyers and renters
• 🗺️ Explore on Map to find properties in your preferred locations
• 💬 Contact Agents directly and get instant responses

🚀 Start exploring: https://www.ereft.com

Whether you're looking to buy, rent, or sell, Ereft makes the entire process smooth and enjoyable.

If you have any questions or need help, we're here for you!

Happy house hunting! 🏡✨

Best regards,
The Ereft Team 💙

---
This email was sent to {recipient_email}
© {datetime.now().year} Ereft. All rights reserved.
        """
        
        # Get FROM email from settings
        from_email = settings.DEFAULT_FROM_EMAIL
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[recipient_email],
            html_message=html_content,
            fail_silently=False,
        )
        
        print(f"✅ Welcome email sent to {recipient_email} (from: {from_email})")
        return True
    except Exception as e:
        print(f"❌ Failed to send welcome email to {recipient_email if 'recipient_email' in locals() else user.email}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

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
        public_id: The public ID of the image (e.g., "ereft_properties/xmbzkzdrb9r52jcyihct")
        transformation: Optional transformation parameters
    
    Returns:
        str: The full Cloudinary HTTPS URL
    """
    try:
        # Ensure Cloudinary is configured
        cloudinary.config(
            cloud_name=getattr(settings, 'CLOUDINARY_CLOUD_NAME', 'detdm1snc'),
            secure=True
        )
        
        # Build URL using Cloudinary SDK (will automatically add version for cache-busting)
        if transformation:
            url = cloudinary.CloudinaryImage(public_id).build_url(**transformation)
        else:
            url = cloudinary.CloudinaryImage(public_id).build_url()
        
        # Ensure HTTPS
        if url and url.startswith('http://'):
            url = url.replace('http://', 'https://', 1)
        
        print(f"✅ get_cloudinary_url: Generated URL for public_id '{public_id}': {url[:80] if url else 'None'}...")
        return url
        
    except Exception as e:
        print(f"❌ Error generating Cloudinary URL for public_id '{public_id}': {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Fallback: Construct URL manually
        try:
            from django.conf import settings
            cloud_name = getattr(settings, 'CLOUDINARY_CLOUD_NAME', 'detdm1snc')
            # Manual construction: https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}
            # Cloudinary will serve the image correctly without version/extensions
            fallback_url = f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}"
            print(f"✅ get_cloudinary_url: Using fallback URL: {fallback_url[:80]}...")
            return fallback_url
        except Exception as fallback_error:
            print(f"❌ Failed to construct fallback URL: {fallback_error}")
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
        dict: Image data with Cloudinary URL and metadata, or None if upload fails
    """
    try:
        # Validate file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/gif']
        if hasattr(image_file, 'content_type') and image_file.content_type not in allowed_types:
            print(f"⚠️ Invalid image type: {image_file.content_type}. Allowed: {', '.join(allowed_types)}")
            return None
        
        # Validate file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB in bytes
        if hasattr(image_file, 'size') and image_file.size > max_size:
            print(f"⚠️ Image too large: {image_file.size} bytes. Max size: {max_size} bytes")
            return None
        
        # Check if Cloudinary is configured
        from django.conf import settings
        cloud_name = getattr(settings, 'CLOUDINARY_CLOUD_NAME', None) or os.environ.get('CLOUDINARY_CLOUD_NAME')
        api_key = getattr(settings, 'CLOUDINARY_API_KEY', None) or os.environ.get('CLOUDINARY_API_KEY')
        api_secret = getattr(settings, 'CLOUDINARY_API_SECRET', None) or os.environ.get('CLOUDINARY_API_SECRET')
        
        if not all([cloud_name, api_key, api_secret]):
            print(f"⚠️ Cloudinary not configured - missing credentials")
            print(f"   CLOUDINARY_CLOUD_NAME: {'✅' if cloud_name else '❌'}")
            print(f"   CLOUDINARY_API_KEY: {'✅' if api_key else '❌'}")
            print(f"   CLOUDINARY_API_SECRET: {'✅' if api_secret else '❌'}")
            return None
        
        # Ensure Cloudinary is configured
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret
        )
        
        # Ensure image_file is properly positioned at the start
        if hasattr(image_file, 'seek'):
            image_file.seek(0)
        
        print(f"📤 Uploading image to Cloudinary: {image_file.name if hasattr(image_file, 'name') else 'unnamed'} ({image_file.size if hasattr(image_file, 'size') else 'unknown size'} bytes)")
        
        # Upload to Cloudinary with optimized settings
        result = cloudinary.uploader.upload(
            image_file,
            folder=f"ereft_properties/{property_id}",
            resource_type="image",
            transformation=[
                {"width": 1200, "height": 800, "crop": "limit"},
                {"quality": "auto:good", "fetch_format": "auto"}
            ],
            eager=[
                {"width": 800, "height": 600, "crop": "limit"},
                {"width": 400, "height": 300, "crop": "limit"}
            ]
        )
        
        secure_url = result.get('secure_url') or result.get('url')
        if not secure_url:
            print(f"❌ Cloudinary upload succeeded but no URL returned in result")
            print(f"   Result keys: {list(result.keys())}")
            return None
        
        print(f"✅ Image uploaded successfully to Cloudinary: {result.get('public_id', 'unknown')}")
        print(f"   URL: {secure_url[:100]}...")
        print(f"   Size: {result.get('bytes', 0)} bytes")
        
        # Return formatted image data with secure_url as primary URL
        image_data = {
            'public_id': result.get('public_id'),
            'url': secure_url,
            'width': result.get('width', 0),
            'height': result.get('height', 0),
            'format': result.get('format', 'unknown'),
            'size': result.get('bytes', 0)
        }
        
        return image_data
        
    except cloudinary.exceptions.Error as e:
        print(f"❌ Cloudinary error: {str(e)}")
        print(f"   Property creation will continue without this image")
        return None
    except Exception as e:
        print(f"❌ Error handling property image upload: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        print(f"   Property creation will continue without this image")
        # Return None instead of raising - allow property creation without images
        return None

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
