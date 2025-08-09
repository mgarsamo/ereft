web: python manage.py migrate && gunicorn wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 120
