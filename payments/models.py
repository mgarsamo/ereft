from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import uuid

class Payment(models.Model):
    """
    Payment model for tracking Stripe payments
    """
    PAYMENT_TYPES = [
        ('featured_listing', 'Featured Listing'),
        ('subscription', 'Subscription'),
        ('premium_feature', 'Premium Feature'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='ETB')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Stripe specific fields
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Related objects
    property = models.ForeignKey('listings.Property', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Metadata
    description = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {self.id} - {self.user.username} - {self.amount} {self.currency}"

class Subscription(models.Model):
    """
    Subscription model for recurring payments
    """
    SUBSCRIPTION_TYPES = [
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('past_due', 'Past Due'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    subscription_type = models.CharField(max_length=20, choices=SUBSCRIPTION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Stripe specific fields
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Subscription details
    current_period_start = models.DateTimeField(blank=True, null=True)
    current_period_end = models.DateTimeField(blank=True, null=True)
    cancel_at_period_end = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Subscription {self.user.username} - {self.subscription_type}"

class PromoCode(models.Model):
    """
    Promotional codes for discounts
    """
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    max_uses = models.PositiveIntegerField(default=1)
    current_uses = models.PositiveIntegerField(default=0)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Promo Code: {self.code} - {self.discount_percentage}% off"
    
    def is_valid(self):
        """Check if promo code is valid"""
        from django.utils import timezone
        now = timezone.now()
        return (
            self.is_active and
            self.current_uses < self.max_uses and
            self.valid_from <= now <= self.valid_until
        )
    
    def use_code(self):
        """Mark promo code as used"""
        if self.is_valid():
            self.current_uses += 1
            self.save()
            return True
        return False

class PaymentMethod(models.Model):
    """
    User's saved payment methods
    """
    PAYMENT_METHOD_TYPES = [
        ('card', 'Credit/Debit Card'),
        ('bank_account', 'Bank Account'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    payment_method_type = models.CharField(max_length=20, choices=PAYMENT_METHOD_TYPES)
    stripe_payment_method_id = models.CharField(max_length=255)
    
    # Card details (masked)
    last4 = models.CharField(max_length=4, blank=True, null=True)
    brand = models.CharField(max_length=20, blank=True, null=True)
    exp_month = models.PositiveIntegerField(blank=True, null=True)
    exp_year = models.PositiveIntegerField(blank=True, null=True)
    
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"Payment Method {self.user.username} - {self.payment_method_type}"
