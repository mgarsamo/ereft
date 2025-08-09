# FILE: ereft_api/wsgi.py

import os
from django.core.wsgi import get_wsgi_application

# ✅ Use the flat layout module path — settings.py is in the same folder
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

application = get_wsgi_application()
