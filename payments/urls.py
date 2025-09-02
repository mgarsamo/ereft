from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'payments', views.PaymentViewSet, basename='payment')
router.register(r'subscriptions', views.SubscriptionViewSet, basename='subscription')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Payment intent creation
    path('create-payment-intent/', views.CreatePaymentIntentView.as_view(), name='create-payment-intent'),
    
    # Webhook for Stripe events
    path('webhook/', views.PaymentWebhookView.as_view(), name='payment-webhook'),
    
    # Promo code validation
    path('promo-code/', views.PromoCodeView.as_view(), name='promo-code'),
    
    # Subscription management
    path('create-subscription/', views.create_subscription, name='create-subscription'),
    path('cancel-subscription/', views.cancel_subscription, name='cancel-subscription'),
]
