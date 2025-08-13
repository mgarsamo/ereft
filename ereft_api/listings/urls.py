# FILE: ereft_api/listings/urls.py
# MINIMAL TEST: Testing if Django can load URLs at all
# TIMESTAMP: 2025-01-15 15:45:00

from django.urls import path
from django.http import JsonResponse
from datetime import datetime

urlpatterns = [
    # MINIMAL TEST: Just one simple endpoint
    path('minimal-test/', lambda request: JsonResponse({
        'message': 'Django is loading listings URLs correctly',
        'timestamp': str(datetime.now()),
        'status': 'SUCCESS'
    }), name='minimal-test'),
]
