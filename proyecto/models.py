from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django_pandas.managers import DataFrameManager


#Modelo Usuario:
#   CAMPOS: id_usuario (clave primaria), nombre, email (único), contraseña_hash, fecha_registro
#   REPRESENTACIÓN: nombre del usuario
class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    contrasena_hash = models.CharField(max_length=255)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()
    df = DataFrameManager()

    class Meta:
        db_table = "usuarios"

    def __str__(self):
        return self.nombre


#Modelo Categoría:
#   CAMPOS: id_categoría (clave primaria), nombre (único), descripción
#   ORDENAR POR nombre ascendente
#   REPRESENTACIÓN: nombre de la categoría
class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    objects = models.Manager()
    df = DataFrameManager()

    class Meta:
        db_table = "categorias"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


#Modelo Ingrediente:
#   CAMPOS: id_ingrediente (clave primaria), nombre (único), unidad_base
#   ORDENAR POR nombre ascendente
#   REPRESENTACIÓN: nombre del ingrediente
class Ingrediente(models.Model):
    id_ingrediente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    unidad_base = models.CharField(max_length=50)

    objects = models.Manager()
    df = DataFrameManager()

    class Meta:
        db_table = "ingredientes"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


#Modelo Receta:
#   CAMPOS: id_receta (clave primaria), usuario (FK→Usuario), categoría (FK→Categoría),
#           título, descripción, instrucciones, tiempo_preparación, dificultad, fecha_creación
#   RELACIONES: ingredientes (N:M a través de RecetaIngrediente), favoritos (N:M a través de Favorito)
#   ORDENAR POR fecha_creación descendente
#   puntuación_media():
#       comentarios ← OBTENER todos los comentarios de esta receta
#       SI NO hay comentarios: RETORNAR 0
#       RETORNAR SUMA(puntuaciones) / cantidad_comentarios REDONDEADO a 1 decimal
class Receta(models.Model):
    class Dificultad(models.TextChoices):
        FACIL = "facil", "Fácil"
        MEDIA = "media", "Media"
        DIFICIL = "dificil", "Difícil"

    id_receta = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column="id_usuario",
        related_name="recetas",
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        db_column="id_categoria",
        related_name="recetas",
        null=True,
        blank=True,
    )
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    instrucciones = models.TextField()
    tiempo_preparacion = models.PositiveIntegerField(
        help_text="Tiempo en minutos"
    )
    dificultad = models.CharField(
        max_length=10,
        choices=Dificultad.choices,
        default=Dificultad.MEDIA,
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    ingredientes = models.ManyToManyField(
        Ingrediente,
        through="RecetaIngrediente",
        related_name="recetas",
    )
    favoritos = models.ManyToManyField(
        Usuario,
        through="Favorito",
        related_name="recetas_favoritas",
    )

    objects = models.Manager()
    df = DataFrameManager()

    class Meta:
        db_table = "recetas"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return self.titulo

    def puntuacion_media(self):
        comentarios = self.comentarios.all()
        if not comentarios.exists():
            return 0
        total = sum(c.puntuacion for c in comentarios)
        return round(total / comentarios.count(), 1)


#Modelo RecetaIngrediente (tabla intermedia):
#   CAMPOS: receta (FK→Receta), ingrediente (FK→Ingrediente), cantidad, unidad, opcional
#   RESTRICCIÓN: combinación (receta, ingrediente) debe ser única
class RecetaIngrediente(models.Model):
    receta = models.ForeignKey(
        Receta,
        on_delete=models.CASCADE,
        db_column="id_receta",
        related_name="receta_ingredientes",
    )
    ingrediente = models.ForeignKey(
        Ingrediente,
        on_delete=models.CASCADE,
        db_column="id_ingrediente",
        related_name="receta_ingredientes",
    )
    cantidad = models.DecimalField(max_digits=8, decimal_places=2)
    unidad = models.CharField(max_length=50)
    opcional = models.BooleanField(default=False)

    objects = models.Manager()
    df = DataFrameManager()

    class Meta:
        db_table = "receta_ingrediente"
        constraints = [
            models.UniqueConstraint(
                fields=["receta", "ingrediente"],
                name="pk_receta_ingrediente",
            )
        ]

    def __str__(self):
        return f"{self.cantidad} {self.unidad} de {self.ingrediente}"


#Modelo ImagenReceta:
#   CAMPOS: id_imagen (clave primaria), receta (FK→Receta), url_imagen, texto_alternativo, es_principal
class ImagenReceta(models.Model):
    id_imagen = models.AutoField(primary_key=True)
    receta = models.ForeignKey(
        Receta,
        on_delete=models.CASCADE,
        db_column="id_receta",
        related_name="imagenes",
    )
    url_imagen = models.URLField(max_length=500)
    texto_alternativo = models.CharField(max_length=255, blank=True)
    es_principal = models.BooleanField(default=False)

    objects = models.Manager()
    df = DataFrameManager()

    class Meta:
        db_table = "imagenes_receta"

    def __str__(self):
        return f"Imagen de {self.receta}"


#Modelo Comentario:
#   CAMPOS: id_comentario (clave primaria), usuario (FK→Usuario), receta (FK→Receta),
#           contenido, puntuación (1-5), fecha_comentario
#   ORDENAR POR fecha_comentario descendente
class Comentario(models.Model):
    id_comentario = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column="id_usuario",
        related_name="comentarios",
    )
    receta = models.ForeignKey(
        Receta,
        on_delete=models.CASCADE,
        db_column="id_receta",
        related_name="comentarios",
    )
    contenido = models.TextField()
    puntuacion = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    fecha_comentario = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()
    df = DataFrameManager()

    class Meta:
        db_table = "comentarios"
        ordering = ["-fecha_comentario"]

    def __str__(self):
        return f"Comentario de {self.usuario} en {self.receta}"


#Modelo Favorito:
#   CAMPOS: usuario (FK→Usuario), receta (FK→Receta), fecha_guardado
#   RESTRICCIÓN: combinación (usuario, receta) debe ser única
class Favorito(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column="id_usuario",
        related_name="favoritos",
    )
    receta = models.ForeignKey(
        Receta,
        on_delete=models.CASCADE,
        db_column="id_receta",
        related_name="guardado_por",
    )
    fecha_guardado = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()
    df = DataFrameManager()

    class Meta:
        db_table = "favoritos"
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "receta"],
                name="pk_favoritos",
            )
        ]

    def __str__(self):
        return f"{self.usuario} guardó {self.receta}"
