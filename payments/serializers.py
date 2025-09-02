from rest_framework import serializers
from .models import Payment, Subscription, PromoCode, PaymentMethod

class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for Payment model
    """
    property_title = serializers.CharField(source='property.title', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'user_username', 'amount', 'currency', 'payment_type',
            'status', 'property', 'property_title', 'description', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'stripe_payment_intent_id', 'created_at']

class CreatePaymentIntentSerializer(serializers.Serializer):
    """
    Serializer for creating payment intent
    """
    property_id = serializers.UUIDField()
    promo_code = serializers.CharField(required=False, allow_blank=True)

class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for Subscription model
    """
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'user', 'user_username', 'user_email', 'subscription_type',
            'status', 'current_period_start', 'current_period_end',
            'cancel_at_period_end', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'stripe_subscription_id', 'created_at']

class PromoCodeSerializer(serializers.ModelSerializer):
    """
    Serializer for PromoCode model
    """
    is_valid = serializers.SerializerMethodField()
    
    class Meta:
        model = PromoCode
        fields = [
            'id', 'code', 'description', 'discount_percentage', 'max_uses',
            'current_uses', 'valid_from', 'valid_until', 'is_active', 'is_valid'
        ]
        read_only_fields = ['id', 'current_uses', 'is_valid']
    
    def get_is_valid(self, obj):
        return obj.is_valid()

class PaymentMethodSerializer(serializers.ModelSerializer):
    """
    Serializer for PaymentMethod model
    """
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'user', 'user_username', 'payment_method_type',
            'last4', 'brand', 'exp_month', 'exp_year', 'is_default',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'stripe_payment_method_id', 'created_at']

class CreateSubscriptionSerializer(serializers.Serializer):
    """
    Serializer for creating subscription
    """
    subscription_type = serializers.ChoiceField(
        choices=Subscription.SUBSCRIPTION_TYPES
    )
    payment_method_id = serializers.CharField(required=False)

class PaymentWebhookSerializer(serializers.Serializer):
    """
    Serializer for payment webhook data
    """
    type = serializers.CharField()
    data = serializers.JSONField()
