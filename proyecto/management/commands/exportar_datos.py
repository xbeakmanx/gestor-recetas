from django.core.management.base import BaseCommand
from proyecto.services import ExportService


class Command(BaseCommand):
    help = "Exporta los datos de la base de datos a CSV y XLSX"

    def add_arguments(self, parser):
        parser.add_argument(
            "--formato",
            choices=["csv", "xlsx", "ambos"],
            default="ambos",
            help="Formato de exportacion (por defecto: ambos)",
        )
        parser.add_argument(
            "--destino",
            default="exportado",
            help="Carpeta de destino (por defecto: exportado/)",
        )

    def handle(self, *args, **options):
        formato = options["formato"]
        destino = options["destino"]

        try:
            if formato == "csv":
                ExportService.exportar_csv(destino)
            elif formato == "xlsx":
                ExportService.exportar_xlsx(destino)
            else:
                ExportService.exportar_todo(destino)
            self.stdout.write(self.style.SUCCESS(
                f"Exportacion completada en carpeta '{destino}/'."
            ))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error al exportar: {e}"))
