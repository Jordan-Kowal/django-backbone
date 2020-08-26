"""
WSGI config for our project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

# Built-in
import os

# Django
from django.core.wsgi import get_wsgi_application

# --------------------------------------------------------------------------------
# > Main
# --------------------------------------------------------------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server_config.settings")
application = get_wsgi_application()
