"""
WSGI config for Optimizing_Battery_Performance_in_Electric_Vehicles_through_Predictive_Modeling project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Optimizing_Battery_Performance_in_Electric_Vehicles_through_Predictive_Modeling.settings')

application = get_wsgi_application()
