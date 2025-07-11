# """
# WSGI config for dentist_project project.

# It exposes the WSGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
# """

# import os

# from django.core.wsgi import get_wsgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dentist_project.settings')

# application = get_wsgi_application()

"""
WSGI config for dentist_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dentist_project.settings')

application = get_wsgi_application()

# 💡 MÜVƏQQƏTİ MİGRATE ƏMRİ:
import django
from django.core.management import call_command

django.setup()
call_command("migrate")
