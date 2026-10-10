import os
import subprocess
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto.settings')

base_dir = Path(__file__).resolve().parent.parent
staticfiles_dir = base_dir / 'staticfiles'
db_path = base_dir / 'db.sqlite3'

if not staticfiles_dir.exists() or not db_path.exists():
    subprocess.run(['python', 'manage.py', 'collectstatic', '--noinput'], cwd=str(base_dir))
    subprocess.run(['python', 'manage.py', 'migrate', '--run-syncdb'], cwd=str(base_dir))
    subprocess.run(['python', 'manage.py', 'cargar_datos'], cwd=str(base_dir))

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
app = application
