"""
ASGI config for Optimizing_Battery_Performance_in_Electric_Vehicles_through_Predictive_Modeling project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Optimizing_Battery_Performance_in_Electric_Vehicles_through_Predictive_Modeling.settings')

application = get_asgi_application()
