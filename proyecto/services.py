import logging
from pathlib import Path

import pandas as pd
from django.db.models import Avg, Count, Q

from .models import (
    Receta, Categoria, Ingrediente, Usuario,
    RecetaIngrediente, ImagenReceta, Comentario, Favorito,
)

logger = logging.getLogger("proyecto")


class RecetaService:
    @staticmethod
    def listar(filtros=None):
        qs = Receta.objects.select_related("usuario", "categoria")
        if filtros:
            if filtros.get("categoria"):
                qs = qs.filter(categoria__id_categoria=filtros["categoria"])
            if filtros.get("dificultad"):
                qs = qs.filter(dificultad=filtros["dificultad"])
            if filtros.get("busqueda"):
                termino = filtros["busqueda"]
                qs = qs.filter(
                    Q(titulo__icontains=termino) |
                    Q(descripcion__icontains=termino)
                )
        logger.info("Listando recetas con %d resultados", qs.count())
        return qs

    @staticmethod
    def obtener(pk):
        try:
            receta = Receta.objects.select_related(
                "usuario", "categoria"
            ).prefetch_related(
                "receta_ingredientes__ingrediente",
                "imagenes",
                "comentarios__usuario",
            ).get(pk=pk)
            logger.info("Receta obtenida: %s", receta.titulo)
            return receta
        except Receta.DoesNotExist:
            logger.warning("Receta con pk=%s no encontrada", pk)
            return None

    @staticmethod
    def crear(datos, ingredientes_data=None):
        try:
            receta = Receta.objects.create(**datos)
            if ingredientes_data:
                for ing_data in ingredientes_data:
                    RecetaIngrediente.objects.create(receta=receta, **ing_data)
            logger.info("Receta creada: %s (pk=%s)", receta.titulo, receta.pk)
            return receta
        except Exception as e:
            logger.error("Error al crear receta: %s", str(e))
            raise

    @staticmethod
    def actualizar(receta, datos):
        try:
            for campo, valor in datos.items():
                setattr(receta, campo, valor)
            receta.save()
            logger.info("Receta actualizada: %s", receta.titulo)
            return receta
        except Exception as e:
            logger.error("Error al actualizar receta pk=%s: %s", receta.pk, str(e))
            raise

    @staticmethod
    def eliminar(receta):
        titulo = receta.titulo
        pk = receta.pk
        try:
            receta.delete()
            logger.info("Receta eliminada: %s (pk=%s)", titulo, pk)
        except Exception as e:
            logger.error("Error al eliminar receta pk=%s: %s", pk, str(e))
            raise

    @staticmethod
    def estadisticas():
        return {
            "total_recetas": Receta.objects.count(),
            "total_usuarios": Usuario.objects.count(),
            "total_categorias": Categoria.objects.count(),
            "total_ingredientes": Ingrediente.objects.count(),
            "total_comentarios": Comentario.objects.count(),
            "puntuacion_media": Comentario.objects.aggregate(
                media=Avg("puntuacion")
            )["media"] or 0,
            "recetas_por_categoria": list(
                Categoria.objects.annotate(
                    num_recetas=Count("recetas")
                ).values("nombre", "num_recetas").order_by("-num_recetas")
            ),
        }


class ExportService:
    MODELOS = {
        "usuarios": Usuario,
        "categorias": Categoria,
        "ingredientes": Ingrediente,
        "recetas": Receta,
        "receta_ingrediente": RecetaIngrediente,
        "imagenes_receta": ImagenReceta,
        "comentarios": Comentario,
        "favoritos": Favorito,
    }

    @classmethod
    def exportar_csv(cls, destino):
        destino = Path(destino)
        destino.mkdir(exist_ok=True)
        archivos = []
        for nombre, modelo in cls.MODELOS.items():
            df = modelo.df.all().to_dataframe()
            ruta = destino / f"{nombre}.csv"
            df.to_csv(ruta, index=False, encoding="utf-8-sig")
            archivos.append(ruta)
            logger.info("CSV exportado: %s (%d filas)", ruta, len(df))
        return archivos

    @classmethod
    def exportar_xlsx(cls, destino):
        destino = Path(destino)
        destino.mkdir(exist_ok=True)
        ruta = destino / "recetas.xlsx"
        with pd.ExcelWriter(ruta, engine="openpyxl") as writer:
            for nombre, modelo in cls.MODELOS.items():
                df = modelo.df.all().to_dataframe()
                df.to_excel(writer, sheet_name=nombre[:31], index=False)
                logger.info("Hoja XLSX: %s (%d filas)", nombre, len(df))
        logger.info("XLSX exportado: %s", ruta)
        return ruta

    @classmethod
    def exportar_todo(cls, destino):
        csvs = cls.exportar_csv(destino)
        xlsx = cls.exportar_xlsx(destino)
        return csvs, xlsx
