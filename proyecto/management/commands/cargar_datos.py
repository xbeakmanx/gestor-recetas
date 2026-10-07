from django.core.management.base import BaseCommand
from proyecto.models import (
    Usuario, Categoria, Ingrediente, Receta,
    RecetaIngrediente, ImagenReceta, Comentario, Favorito,
)


class Command(BaseCommand):
    help = "Carga datos de ejemplo en la base de datos"

    def handle(self, *args, **options):
        for modelo in (Comentario, Favorito, RecetaIngrediente,
                       ImagenReceta, Receta, Ingrediente, Categoria, Usuario):
            modelo.objects.all().delete()

        ana = Usuario.objects.create(
            nombre="Ana Garcia", email="ana@ejemplo.com",
            contrasena_hash="hash_ana",
        )
        luis = Usuario.objects.create(
            nombre="Luis Perez", email="luis@ejemplo.com",
            contrasena_hash="hash_luis",
        )
        maria = Usuario.objects.create(
            nombre="Maria Lopez", email="maria@ejemplo.com",
            contrasena_hash="hash_maria",
        )

        postres = Categoria.objects.create(nombre="Postres", descripcion="Recetas dulces")
        principales = Categoria.objects.create(nombre="Platos principales", descripcion="Comidas fuertes")
        entrantes = Categoria.objects.create(nombre="Entrantes", descripcion="Aperitivos y entrantes")
        bebidas = Categoria.objects.create(nombre="Bebidas", descripcion="Bebidas y batidos")

        harina = Ingrediente.objects.create(nombre="Harina", unidad_base="g")
        azucar = Ingrediente.objects.create(nombre="Azucar", unidad_base="g")
        huevo = Ingrediente.objects.create(nombre="Huevo", unidad_base="unidad")
        arroz = Ingrediente.objects.create(nombre="Arroz", unidad_base="g")
        tomate = Ingrediente.objects.create(nombre="Tomate", unidad_base="unidad")
        aceite = Ingrediente.objects.create(nombre="Aceite de oliva", unidad_base="ml")
        sal = Ingrediente.objects.create(nombre="Sal", unidad_base="g")
        leche = Ingrediente.objects.create(nombre="Leche", unidad_base="ml")
        pollo = Ingrediente.objects.create(nombre="Pechuga de pollo", unidad_base="g")
        limon = Ingrediente.objects.create(nombre="Limon", unidad_base="unidad")

        bizcocho = Receta.objects.create(
            usuario=ana, categoria=postres,
            titulo="Bizcocho casero",
            descripcion="Un bizcocho esponjoso y facil de preparar.",
            instrucciones="1. Precalentar el horno a 180 grados.\n2. Mezclar harina, azucar y huevos.\n3. Verter en molde engrasado.\n4. Hornear 40 minutos.",
            tiempo_preparacion=50, dificultad=Receta.Dificultad.FACIL,
        )
        paella = Receta.objects.create(
            usuario=luis, categoria=principales,
            titulo="Paella valenciana",
            descripcion="Paella tradicional con pollo y verduras.",
            instrucciones="1. Sofreir el pollo troceado.\n2. Anadir tomate rallado.\n3. Anadir agua y dejar hervir.\n4. Anadir arroz y cocinar 20 minutos.",
            tiempo_preparacion=60, dificultad=Receta.Dificultad.MEDIA,
        )
        ensalada = Receta.objects.create(
            usuario=maria, categoria=entrantes,
            titulo="Ensalada mediterranea",
            descripcion="Ensalada fresca con tomate, aceite de oliva y limon.",
            instrucciones="1. Cortar los tomates en rodajas.\n2. Aliñar con aceite y limon.\n3. Anadir sal al gusto.",
            tiempo_preparacion=10, dificultad=Receta.Dificultad.FACIL,
        )
        limonada = Receta.objects.create(
            usuario=ana, categoria=bebidas,
            titulo="Limonada natural",
            descripcion="Limonada refrescante hecha con limones frescos.",
            instrucciones="1. Exprimir los limones.\n2. Mezclar con agua y azucar.\n3. Servir con hielo.",
            tiempo_preparacion=15, dificultad=Receta.Dificultad.FACIL,
        )
        tortilla = Receta.objects.create(
            usuario=luis, categoria=principales,
            titulo="Tortilla espanola",
            descripcion="Tortilla de patatas clasica.",
            instrucciones="1. Pelar y cortar las patatas.\n2. Freir en aceite.\n3. Batir los huevos y mezclar.\n4. Cuajar en sarten.",
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

        ImagenReceta.objects.create(receta=bizcocho, url_imagen="https://ejemplo.com/bizcocho.jpg", texto_alternativo="Bizcocho casero", es_principal=True)
        ImagenReceta.objects.create(receta=paella, url_imagen="https://ejemplo.com/paella.jpg", texto_alternativo="Paella valenciana", es_principal=True)

        Comentario.objects.create(usuario=luis, receta=bizcocho, contenido="Muy rico y facil de hacer.", puntuacion=5)
        Comentario.objects.create(usuario=maria, receta=bizcocho, contenido="Le anadí chocolate y quedo genial.", puntuacion=4)
        Comentario.objects.create(usuario=ana, receta=paella, contenido="Me quedo buenisima.", puntuacion=4)
        Comentario.objects.create(usuario=maria, receta=paella, contenido="Un clasico que nunca falla.", puntuacion=5)
        Comentario.objects.create(usuario=luis, receta=ensalada, contenido="Perfecta para el verano.", puntuacion=4)
        Comentario.objects.create(usuario=ana, receta=tortilla, contenido="La mejor receta de tortilla.", puntuacion=5)

        Favorito.objects.create(usuario=ana, receta=paella)
        Favorito.objects.create(usuario=luis, receta=bizcocho)
        Favorito.objects.create(usuario=maria, receta=ensalada)
        Favorito.objects.create(usuario=maria, receta=limonada)

        self.stdout.write(self.style.SUCCESS("Datos de ejemplo cargados correctamente."))
