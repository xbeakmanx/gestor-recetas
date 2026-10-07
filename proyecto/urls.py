from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Inicio
    path('', views.InicioView.as_view(), name='inicio'),

    # Recetas
    path('recetas/', views.RecetaListView.as_view(), name='receta_lista'),
    path('recetas/nueva/', views.RecetaCreateView.as_view(), name='receta_crear'),
    path('recetas/<int:pk>/', views.RecetaDetailView.as_view(), name='receta_detalle'),
    path('recetas/<int:pk>/editar/', views.RecetaUpdateView.as_view(), name='receta_editar'),
    path('recetas/<int:pk>/eliminar/', views.RecetaDeleteView.as_view(), name='receta_eliminar'),

    # Categorias
    path('categorias/', views.CategoriaListView.as_view(), name='categoria_lista'),
    path('categorias/nueva/', views.CategoriaCreateView.as_view(), name='categoria_crear'),
    path('categorias/<int:pk>/editar/', views.CategoriaUpdateView.as_view(), name='categoria_editar'),
    path('categorias/<int:pk>/eliminar/', views.CategoriaDeleteView.as_view(), name='categoria_eliminar'),

    # Ingredientes
    path('ingredientes/', views.IngredienteListView.as_view(), name='ingrediente_lista'),
    path('ingredientes/nuevo/', views.IngredienteCreateView.as_view(), name='ingrediente_crear'),
    path('ingredientes/<int:pk>/editar/', views.IngredienteUpdateView.as_view(), name='ingrediente_editar'),
    path('ingredientes/<int:pk>/eliminar/', views.IngredienteDeleteView.as_view(), name='ingrediente_eliminar'),

    # Comentarios
    path('recetas/<int:receta_pk>/comentar/', views.ComentarioCreateView.as_view(), name='comentario_crear'),

    # Exportacion
    path('exportar/', views.ExportarView.as_view(), name='exportar'),
]
