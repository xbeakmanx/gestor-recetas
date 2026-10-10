from django.contrib import admin
from .models import (
    Usuario, Categoria, Ingrediente, Receta,
    RecetaIngrediente, ImagenReceta, Comentario, Favorito,
)


#Configuración del panel de administración:
#   PARA CADA modelo (Usuario, Categoría, Ingrediente, Receta, Comentario, Favorito):
#       REGISTRAR en el admin de Django
#       DEFINIR columnas visibles en la lista
#       DEFINIR campos de búsqueda y filtros
#   Receta incluye líneas inline para editar ingredientes e imágenes directamente
class RecetaIngredienteInline(admin.TabularInline):
    model = RecetaIngrediente
    extra = 1


class ImagenRecetaInline(admin.TabularInline):
    model = ImagenReceta
    extra = 1


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "email", "fecha_registro")
    search_fields = ("nombre", "email")


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion")
    search_fields = ("nombre",)


@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "unidad_base")
    search_fields = ("nombre",)


@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "usuario", "categoria", "dificultad", "tiempo_preparacion", "fecha_creacion")
    list_filter = ("dificultad", "categoria")
    search_fields = ("titulo", "descripcion")
    inlines = [RecetaIngredienteInline, ImagenRecetaInline]


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ("usuario", "receta", "puntuacion", "fecha_comentario")
    list_filter = ("puntuacion",)


@admin.register(Favorito)
class FavoritoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "receta", "fecha_guardado")
