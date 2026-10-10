from django.core.management.base import BaseCommand
from proyecto.models import (
    Usuario, Categoria, Ingrediente, Receta,
    RecetaIngrediente, ImagenReceta, Comentario, Favorito,
)


#cargar_datos():
#   ELIMINAR todos los datos existentes de cada modelo
#   CREAR 3 usuarios de ejemplo (Ana, Luis, María)
#   CREAR 4 categorías (Postres, Platos principales, Entrantes, Bebidas)
#   CREAR 10 ingredientes (Harina, Azúcar, Huevo, Arroz, ...)
#   CREAR 5 recetas con sus datos (Bizcocho, Paella, Ensalada, Limonada, Tortilla)
#   CREAR 18 relaciones receta-ingrediente con cantidades y unidades
#   CREAR 5 imágenes de receta con URLs externas
#   CREAR 6 comentarios con puntuaciones
#   CREAR 4 favoritos
#   MOSTRAR mensaje "Datos de ejemplo cargados correctamente"
class Command(BaseCommand):
    help = "Carga datos de ejemplo en la base de datos"

    def handle(self, *args, **options):
        for modelo in (Comentario, Favorito, RecetaIngrediente,
                       ImagenReceta, Receta, Ingrediente, Categoria, Usuario):
            modelo.objects.all().delete()

        ana = Usuario.objects.create(
            nombre="Ana García", email="ana@ejemplo.com",
            contrasena_hash="hash_ana",
        )
        luis = Usuario.objects.create(
            nombre="Luis Pérez", email="luis@ejemplo.com",
            contrasena_hash="hash_luis",
        )
        maria = Usuario.objects.create(
            nombre="María López", email="maria@ejemplo.com",
            contrasena_hash="hash_maria",
        )

        postres = Categoria.objects.create(nombre="Postres", descripcion="Recetas dulces")
        principales = Categoria.objects.create(nombre="Platos principales", descripcion="Comidas fuertes")
        entrantes = Categoria.objects.create(nombre="Entrantes", descripcion="Aperitivos y entrantes")
        bebidas = Categoria.objects.create(nombre="Bebidas", descripcion="Bebidas y batidos")

        harina = Ingrediente.objects.create(nombre="Harina", unidad_base="g")
        azucar = Ingrediente.objects.create(nombre="Azúcar", unidad_base="g")
        huevo = Ingrediente.objects.create(nombre="Huevo", unidad_base="unidad")
        arroz = Ingrediente.objects.create(nombre="Arroz", unidad_base="g")
        tomate = Ingrediente.objects.create(nombre="Tomate", unidad_base="unidad")
        aceite = Ingrediente.objects.create(nombre="Aceite de oliva", unidad_base="ml")
        sal = Ingrediente.objects.create(nombre="Sal", unidad_base="g")
        leche = Ingrediente.objects.create(nombre="Leche", unidad_base="ml")
        pollo = Ingrediente.objects.create(nombre="Pechuga de pollo", unidad_base="g")
        limon = Ingrediente.objects.create(nombre="Limón", unidad_base="unidad")

        bizcocho = Receta.objects.create(
            usuario=ana, categoria=postres,
            titulo="Bizcocho casero",
            descripcion="Un bizcocho esponjoso y fácil de preparar.",
            instrucciones="1. Precalentar el horno a 180 grados.\n2. Mezclar harina, azúcar y huevos.\n3. Verter en molde engrasado.\n4. Hornear 40 minutos.",
            tiempo_preparacion=50, dificultad=Receta.Dificultad.FACIL,
        )
        paella = Receta.objects.create(
            usuario=luis, categoria=principales,
            titulo="Paella valenciana",
            descripcion="Paella tradicional con pollo y verduras.",
            instrucciones="1. Sofreír el pollo troceado.\n2. Añadir tomate rallado.\n3. Añadir agua y dejar hervir.\n4. Añadir arroz y cocinar 20 minutos.",
            tiempo_preparacion=60, dificultad=Receta.Dificultad.MEDIA,
        )
        ensalada = Receta.objects.create(
            usuario=maria, categoria=entrantes,
            titulo="Ensalada mediterránea",
            descripcion="Ensalada fresca con tomate, aceite de oliva y limón.",
            instrucciones="1. Cortar los tomates en rodajas.\n2. Aliñar con aceite y limón.\n3. Añadir sal al gusto.",
            tiempo_preparacion=10, dificultad=Receta.Dificultad.FACIL,
        )
        limonada = Receta.objects.create(
            usuario=ana, categoria=bebidas,
            titulo="Limonada natural",
            descripcion="Limonada refrescante hecha con limones frescos.",
            instrucciones="1. Exprimir los limones.\n2. Mezclar con agua y azúcar.\n3. Servir con hielo.",
            tiempo_preparacion=15, dificultad=Receta.Dificultad.FACIL,
        )
        tortilla = Receta.objects.create(
            usuario=luis, categoria=principales,
            titulo="Tortilla española",
            descripcion="Tortilla de patatas clásica.",
            instrucciones="1. Pelar y cortar las patatas.\n2. Freír en aceite.\n3. Batir los huevos y mezclar.\n4. Cuajar en sartén.",
            tiempo_preparacion=40, dificultad=Receta.Dificultad.MEDIA,
        )

        RecetaIngrediente.objects.create(receta=bizcocho, ingrediente=harina, cantidad=250, unidad="g")
        RecetaIngrediente.objects.create(receta=bizcocho, ingrediente=azucar, cantidad=200, unidad="g")
        RecetaIngrediente.objects.create(receta=bizcocho, ingrediente=huevo, cantidad=3, unidad="unidad")
        RecetaIngrediente.objects.create(receta=bizcocho, ingrediente=leche, cantidad=100, unidad="ml")
        RecetaIngrediente.objects.create(receta=paella, ingrediente=arroz, cantidad=400, unidad="g")
        RecetaIngrediente.objects.create(receta=paella, ingrediente=pollo, cantidad=500, unidad="g")
        RecetaIngrediente.objects.create(receta=paella, ingrediente=tomate, cantidad=2, unidad="unidad")
        RecetaIngrediente.objects.create(receta=paella, ingrediente=aceite, cantidad=50, unidad="ml")
        RecetaIngrediente.objects.create(receta=paella, ingrediente=sal, cantidad=10, unidad="g")
        RecetaIngrediente.objects.create(receta=ensalada, ingrediente=tomate, cantidad=4, unidad="unidad")
        RecetaIngrediente.objects.create(receta=ensalada, ingrediente=aceite, cantidad=30, unidad="ml")
        RecetaIngrediente.objects.create(receta=ensalada, ingrediente=limon, cantidad=1, unidad="unidad")
        RecetaIngrediente.objects.create(receta=ensalada, ingrediente=sal, cantidad=5, unidad="g")
        RecetaIngrediente.objects.create(receta=limonada, ingrediente=limon, cantidad=4, unidad="unidad")
        RecetaIngrediente.objects.create(receta=limonada, ingrediente=azucar, cantidad=100, unidad="g")
        RecetaIngrediente.objects.create(receta=tortilla, ingrediente=huevo, cantidad=6, unidad="unidad")
        RecetaIngrediente.objects.create(receta=tortilla, ingrediente=aceite, cantidad=200, unidad="ml")
        RecetaIngrediente.objects.create(receta=tortilla, ingrediente=sal, cantidad=5, unidad="g")

        ImagenReceta.objects.create(receta=bizcocho, url_imagen="https://images.unsplash.com/photo-1588195538326-c5b1e9f80a1b?w=600", texto_alternativo="Bizcocho casero", es_principal=True)
        ImagenReceta.objects.create(receta=paella, url_imagen="https://images.unsplash.com/photo-1534080564583-6be75777b70a?w=600", texto_alternativo="Paella valenciana", es_principal=True)
        ImagenReceta.objects.create(receta=ensalada, url_imagen="https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=600", texto_alternativo="Ensalada mediterránea", es_principal=True)
        ImagenReceta.objects.create(receta=limonada, url_imagen="https://images.unsplash.com/photo-1621263764928-df1444c5e859?w=600", texto_alternativo="Limonada natural", es_principal=True)
        ImagenReceta.objects.create(receta=tortilla, url_imagen="https://images.unsplash.com/photo-1599789197514-47270cd526b4?w=600", texto_alternativo="Tortilla española", es_principal=True)

        Comentario.objects.create(usuario=luis, receta=bizcocho, contenido="Muy rico y fácil de hacer.", puntuacion=5)
        Comentario.objects.create(usuario=maria, receta=bizcocho, contenido="Le añadí chocolate y quedó genial.", puntuacion=4)
        Comentario.objects.create(usuario=ana, receta=paella, contenido="Me quedó buenísima.", puntuacion=4)
        Comentario.objects.create(usuario=maria, receta=paella, contenido="Un clásico que nunca falla.", puntuacion=5)
        Comentario.objects.create(usuario=luis, receta=ensalada, contenido="Perfecta para el verano.", puntuacion=4)
        Comentario.objects.create(usuario=ana, receta=tortilla, contenido="La mejor receta de tortilla.", puntuacion=5)

        Favorito.objects.create(usuario=ana, receta=paella)
        Favorito.objects.create(usuario=luis, receta=bizcocho)
        Favorito.objects.create(usuario=maria, receta=ensalada)
        Favorito.objects.create(usuario=maria, receta=limonada)

        self.stdout.write(self.style.SUCCESS("Datos de ejemplo cargados correctamente."))
