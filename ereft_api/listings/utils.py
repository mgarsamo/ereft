import os
import uuid
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from PIL import Image
from io import BytesIO
from django.core.files import File
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
    Compress image before saving
    """
    if image_field:
        img = Image.open(image_field)
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if larger than max_size
        if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save compressed image
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        # Generate unique filename
        filename = f"{uuid.uuid4()}.jpg"
        
        return File(output, name=filename)
    
    return None

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
