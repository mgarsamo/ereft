import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, generics
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from .models import Payment, Subscription, PromoCode, PaymentMethod
from .serializers import (
    PaymentSerializer, SubscriptionSerializer, PromoCodeSerializer,
    PaymentMethodSerializer, CreatePaymentIntentSerializer
)
from ereft_api.listings.models import Property
from django.contrib.auth import get_user_model

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for payment management
    """
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

class CreatePaymentIntentView(APIView):
    """
    Create Stripe payment intent for featured listing
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = CreatePaymentIntentSerializer(data=request.data)
        if serializer.is_valid():
            property_id = serializer.validated_data.get('property_id')
            promo_code = serializer.validated_data.get('promo_code')
            
            try:
                property_obj = Property.objects.get(id=property_id, owner=request.user)
            except Property.DoesNotExist:
                return Response(
                    {'error': 'Property not found or not owned by user'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Calculate amount (featured listing fee)
            amount = 5000  # 5000 ETB for featured listing
            
            # Apply promo code discount if valid
            if promo_code:
                try:
                    promo = PromoCode.objects.get(code=promo_code)
                    if promo.is_valid():
                        discount = (amount * promo.discount_percentage) / 100
                        amount = amount - discount
                        promo.use_code()
                except PromoCode.DoesNotExist:
                    return Response(
                        {'error': 'Invalid promo code'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            try:
                # Create Stripe payment intent
                payment_intent = stripe.PaymentIntent.create(
                    amount=int(amount * 100),  # Convert to cents
                    currency='etb',
                    metadata={
                        'property_id': str(property_id),
                        'user_id': str(request.user.id),
                        'payment_type': 'featured_listing'
                    }
                )
                
                # Create payment record
                payment = Payment.objects.create(
                    user=request.user,
                    amount=amount,
                    currency='ETB',
                    payment_type='featured_listing',
                    property=property_obj,
                    stripe_payment_intent_id=payment_intent.id,
                    description=f'Featured listing for {property_obj.title}'
                )
                
                return Response({
                    'client_secret': payment_intent.client_secret,
                    'payment_id': str(payment.id),
                    'amount': amount
                })
                
            except stripe.error.StripeError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PaymentWebhookView(APIView):
    """
    Handle Stripe webhooks
    """
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            return Response({'error': 'Invalid payload'}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Handle the event
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            self.handle_payment_success(payment_intent)
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            self.handle_payment_failure(payment_intent)
        elif event['type'] == 'customer.subscription.created':
            subscription = event['data']['object']
            self.handle_subscription_created(subscription)
        elif event['type'] == 'customer.subscription.updated':
            subscription = event['data']['object']
            self.handle_subscription_updated(subscription)
        
        return Response({'status': 'success'})
    
    def handle_payment_success(self, payment_intent):
        """Handle successful payment"""
        try:
            payment = Payment.objects.get(
                stripe_payment_intent_id=payment_intent['id']
            )
            payment.status = 'completed'
            payment.save()
            
            # Mark property as featured
            if payment.property and payment.payment_type == 'featured_listing':
                payment.property.is_featured = True
                payment.property.save()
                
        except Payment.DoesNotExist:
            pass
    
    def handle_payment_failure(self, payment_intent):
        """Handle failed payment"""
        try:
            payment = Payment.objects.get(
                stripe_payment_intent_id=payment_intent['id']
            )
            payment.status = 'failed'
            payment.save()
        except Payment.DoesNotExist:
            pass
    
    def handle_subscription_created(self, subscription):
        """Handle subscription creation"""
        try:
            user = get_user_model().objects.get(email=subscription['customer_email'])
            Subscription.objects.create(
                user=user,
                subscription_type='premium',  # Default to premium
                status='active',
                stripe_subscription_id=subscription['id'],
                stripe_customer_id=subscription['customer'],
                current_period_start=timezone.datetime.fromtimestamp(
                    subscription['current_period_start']
                ),
                current_period_end=timezone.datetime.fromtimestamp(
                    subscription['current_period_end']
                )
            )
        except get_user_model().DoesNotExist:
            pass
    
    def handle_subscription_updated(self, subscription):
        """Handle subscription updates"""
        try:
            sub = Subscription.objects.get(
                stripe_subscription_id=subscription['id']
            )
            sub.status = subscription['status']
            sub.current_period_start = timezone.datetime.fromtimestamp(
                subscription['current_period_start']
            )
            sub.current_period_end = timezone.datetime.fromtimestamp(
                subscription['current_period_end']
            )
            sub.cancel_at_period_end = subscription['cancel_at_period_end']
            sub.save()
        except Subscription.DoesNotExist:
            pass

class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for subscription management
    """
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

class PromoCodeView(generics.RetrieveAPIView):
    """
    Validate promo code
    """
    serializer_class = PromoCodeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        code = self.request.query_params.get('code')
        return get_object_or_404(PromoCode, code=code)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_subscription(request):
    """
    Create a new subscription
    """
    subscription_type = request.data.get('subscription_type', 'premium')
    
    try:
        # Create Stripe subscription
        subscription = stripe.Subscription.create(
            customer=request.user.stripe_customer_id,
            items=[{'price': settings.STRIPE_PRICE_IDS[subscription_type]}],
            payment_behavior='default_incomplete',
            expand=['latest_invoice.payment_intent'],
        )
        
        # Create local subscription record
        sub = Subscription.objects.create(
            user=request.user,
            subscription_type=subscription_type,
            stripe_subscription_id=subscription.id,
            stripe_customer_id=subscription.customer,
            current_period_start=timezone.datetime.fromtimestamp(
                subscription.current_period_start
            ),
            current_period_end=timezone.datetime.fromtimestamp(
                subscription.current_period_end
            )
        )
        
        return Response({
            'subscription_id': subscription.id,
            'client_secret': subscription.latest_invoice.payment_intent.client_secret
        })
        
    except stripe.error.StripeError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_subscription(request):
    """
    Cancel subscription
    """
    try:
        subscription = Subscription.objects.get(user=request.user)
        
        # Cancel in Stripe
        stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=True
        )
        
        # Update local record
        subscription.cancel_at_period_end = True
        subscription.save()
        
        return Response({'status': 'subscription cancelled'})
        
    except Subscription.DoesNotExist:
        return Response(
            {'error': 'No active subscription found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except stripe.error.StripeError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
