# FILE: ereft_api/asgi.py

"""
ASGI config for Ereft Django app.

Exposes the ASGI callable as a module-level variable named ``application``.

For more information, see:
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

# ✅ Use the correct flat settings path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

application = get_asgi_application()
