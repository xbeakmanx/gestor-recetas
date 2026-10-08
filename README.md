# Gestor de Recetas

Plataforma web para crear, organizar y compartir recetas de cocina. Desarrollada con Django y Python.

## Características

- CRUD completo de recetas, categorías e ingredientes
- Sistema de autenticación con registro e inicio de sesión
- Favoritos: guardar recetas para consultarlas después
- Comentarios con puntuación de 1 a 5 estrellas
- Filtrado por categoría, dificultad y búsqueda por texto
- Exportación de datos a CSV y XLSX con django-pandas
- Diseño responsive con Bootstrap 5
- Logging de acciones en archivo y consola

## Tecnologías

- Python 3.13
- Django 6.1.1
- django-pandas 0.6.7
- pandas 2.2.3
- openpyxl 3.1.5
- SQLite3
- Bootstrap 5 + Bootstrap Icons

## Instalación

```bash
git clone https://github.com/xbeakmanx/gestor-recetas.git
cd gestor-recetas
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py cargar_datos
python manage.py runserver
```

Abrir en el navegador: `http://127.0.0.1:8000/`

## Estructura del proyecto

```
proyecto-recetas/
├── manage.py
├── requirements.txt
├── memoria_tecnica.html
├── proyecto/
│   ├── models.py             # 8 modelos de datos
│   ├── views.py              # Vistas (Class-Based Views)
│   ├── forms.py              # Formularios y validación
│   ├── services.py           # Capa de servicios
│   ├── urls.py               # Rutas URL
│   ├── admin.py              # Panel de administración
│   ├── templatetags/         # Filtros personalizados
│   ├── templates/            # Plantillas HTML
│   ├── static/               # CSS personalizado
│   └── management/commands/  # Comando cargar_datos
```

## Memoria Técnica

La documentación completa del proyecto se encuentra en [`memoria_tecnica.html`](https://htmlpreview.github.io/?https://github.com/xbeakmanx/gestor-recetas/blob/main/memoria_tecnica.html). Incluye:

- Diagrama de arquitectura del sistema
- Diagrama entidad-relación de la base de datos
- Descripción de tecnologías y justificación técnica
- Manual de usuario con instrucciones de instalación y uso
- Detalle de la capa de servicios y exportación de datos
