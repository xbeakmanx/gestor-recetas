import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

try:
    from django.core.management import call_command
    from proyecto.models import Receta
    if Receta.objects.count() < 5:
        call_command('migrate', '--run-syncdb')
        call_command('cargar_datos')
except Exception:
    try:
        call_command('migrate', '--run-syncdb')
        call_command('cargar_datos')
    except Exception:
        pass

app = application
