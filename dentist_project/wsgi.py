import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dentist_project.settings')

application = get_wsgi_application()


# import os
# from django.core.wsgi import get_wsgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dentist_project.settings')

# application = get_wsgi_application()

# # 💡 MÜVƏQQƏTİ MİGRATE ƏMRİ:
# import django
# from django.core.management import call_command

# django.setup()
# call_command("migrate")
