import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponse, Http404

from .models import Receta, Categoria, Ingrediente, Usuario, Comentario, RecetaIngrediente
from .forms import (
    RecetaForm, CategoriaForm, IngredienteForm,
    ComentarioForm, RecetaIngredienteFormSet,
)
from .services import RecetaService, ExportService

logger = logging.getLogger("proyecto")


# --- Mixin para inyectar el usuario por defecto ---

class UsuarioMixin:
    """Obtiene o crea un usuario por defecto para asignar a las operaciones."""

    def get_usuario(self):
        usuario, _ = Usuario.objects.get_or_create(
            email="admin@recetas.com",
            defaults={
                "nombre": "Administrador",
                "contrasena_hash": "no-auth",
            },
        )
        return usuario


# --- Pagina de inicio ---

class InicioView(View):
    def get(self, request):
        try:
            estadisticas = RecetaService.estadisticas()
            ultimas_recetas = Receta.objects.select_related(
                "usuario", "categoria"
            )[:5]
        except Exception as e:
            logger.error("Error al cargar inicio: %s", str(e))
            estadisticas = {}
            ultimas_recetas = []
        return render(request, "proyecto/inicio.html", {
            "estadisticas": estadisticas,
            "ultimas_recetas": ultimas_recetas,
        })


# --- CRUD de Recetas ---

class RecetaListView(ListView):
    model = Receta
    template_name = "proyecto/receta_lista.html"
    context_object_name = "recetas"
    paginate_by = 12

    def get_queryset(self):
        filtros = {
            "categoria": self.request.GET.get("categoria"),
            "dificultad": self.request.GET.get("dificultad"),
            "busqueda": self.request.GET.get("q"),
        }
        return RecetaService.listar(filtros)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categorias"] = Categoria.objects.all()
        context["dificultades"] = Receta.Dificultad.choices
        context["filtros"] = {
            "categoria": self.request.GET.get("categoria", ""),
            "dificultad": self.request.GET.get("dificultad", ""),
            "q": self.request.GET.get("q", ""),
        }
        return context


class RecetaDetailView(DetailView):
    model = Receta
    template_name = "proyecto/receta_detalle.html"
    context_object_name = "receta"

    def get_object(self):
        receta = RecetaService.obtener(self.kwargs["pk"])
        if receta is None:
            raise Http404("Receta no encontrada")
        return receta

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comentario_form"] = ComentarioForm()
        context["ingredientes"] = self.object.receta_ingredientes.select_related("ingrediente")
        return context


class RecetaCreateView(UsuarioMixin, CreateView):
    model = Receta
    form_class = RecetaForm
    template_name = "proyecto/receta_form.html"
    success_url = reverse_lazy("receta_lista")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["formset"] = RecetaIngredienteFormSet(self.request.POST)
        else:
            context["formset"] = RecetaIngredienteFormSet()
        context["titulo_pagina"] = "Nueva Receta"
        return context

    def form_valid(self, form):
        try:
            form.instance.usuario = self.get_usuario()
            context = self.get_context_data()
            formset = context["formset"]
            if formset.is_valid():
                self.object = form.save()
                formset.instance = self.object
                formset.save()
                messages.success(self.request, f"Receta '{self.object.titulo}' creada correctamente.")
                logger.info("Receta creada desde vista: %s", self.object.titulo)
                return redirect(self.success_url)
            else:
                return self.render_to_response(context)
        except Exception as e:
            logger.error("Error al crear receta: %s", str(e))
            messages.error(self.request, "Error al crear la receta. Intentalo de nuevo.")
            return self.form_invalid(form)


class RecetaUpdateView(UpdateView):
    model = Receta
    form_class = RecetaForm
    template_name = "proyecto/receta_form.html"
    success_url = reverse_lazy("receta_lista")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["formset"] = RecetaIngredienteFormSet(
                self.request.POST, instance=self.object
            )
        else:
            context["formset"] = RecetaIngredienteFormSet(instance=self.object)
        context["titulo_pagina"] = "Editar Receta"
        return context

    def form_valid(self, form):
        try:
            context = self.get_context_data()
            formset = context["formset"]
            if formset.is_valid():
                self.object = form.save()
                formset.save()
                messages.success(self.request, f"Receta '{self.object.titulo}' actualizada.")
                logger.info("Receta actualizada: %s", self.object.titulo)
                return redirect(self.success_url)
            else:
                return self.render_to_response(context)
        except Exception as e:
            logger.error("Error al actualizar receta: %s", str(e))
            messages.error(self.request, "Error al actualizar la receta.")
            return self.form_invalid(form)


class RecetaDeleteView(DeleteView):
    model = Receta
    template_name = "proyecto/receta_confirmar_eliminar.html"
    success_url = reverse_lazy("receta_lista")
    context_object_name = "receta"

    def form_valid(self, form):
        titulo = self.object.titulo
        try:
            response = super().form_valid(form)
            messages.success(self.request, f"Receta '{titulo}' eliminada.")
            logger.info("Receta eliminada desde vista: %s", titulo)
            return response
        except Exception as e:
            logger.error("Error al eliminar receta: %s", str(e))
            messages.error(self.request, "Error al eliminar la receta.")
            return redirect(self.success_url)


# --- CRUD de Categorias ---

class CategoriaListView(ListView):
    model = Categoria
    template_name = "proyecto/categoria_lista.html"
    context_object_name = "categorias"


class CategoriaCreateView(CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "proyecto/categoria_form.html"
    success_url = reverse_lazy("categoria_lista")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo_pagina"] = "Nueva Categoria"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Categoria creada correctamente.")
        return super().form_valid(form)


class CategoriaUpdateView(UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "proyecto/categoria_form.html"
    success_url = reverse_lazy("categoria_lista")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo_pagina"] = "Editar Categoria"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Categoria actualizada correctamente.")
        return super().form_valid(form)


class CategoriaDeleteView(DeleteView):
    model = Categoria
    template_name = "proyecto/categoria_confirmar_eliminar.html"
    success_url = reverse_lazy("categoria_lista")
    context_object_name = "categoria"

    def form_valid(self, form):
        messages.success(self.request, "Categoria eliminada.")
        return super().form_valid(form)


# --- CRUD de Ingredientes ---

class IngredienteListView(ListView):
    model = Ingrediente
    template_name = "proyecto/ingrediente_lista.html"
    context_object_name = "ingredientes"


class IngredienteCreateView(CreateView):
    model = Ingrediente
    form_class = IngredienteForm
    template_name = "proyecto/ingrediente_form.html"
    success_url = reverse_lazy("ingrediente_lista")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo_pagina"] = "Nuevo Ingrediente"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Ingrediente creado correctamente.")
        return super().form_valid(form)


class IngredienteUpdateView(UpdateView):
    model = Ingrediente
    form_class = IngredienteForm
    template_name = "proyecto/ingrediente_form.html"
    success_url = reverse_lazy("ingrediente_lista")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo_pagina"] = "Editar Ingrediente"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Ingrediente actualizado correctamente.")
        return super().form_valid(form)


class IngredienteDeleteView(DeleteView):
    model = Ingrediente
    template_name = "proyecto/ingrediente_confirmar_eliminar.html"
    success_url = reverse_lazy("ingrediente_lista")
    context_object_name = "ingrediente"

    def form_valid(self, form):
        messages.success(self.request, "Ingrediente eliminado.")
        return super().form_valid(form)


# --- Comentarios ---

class ComentarioCreateView(UsuarioMixin, View):
    def post(self, request, receta_pk):
        receta = get_object_or_404(Receta, pk=receta_pk)
        form = ComentarioForm(request.POST)
        if form.is_valid():
            try:
                comentario = form.save(commit=False)
                comentario.usuario = self.get_usuario()
                comentario.receta = receta
                comentario.save()
                messages.success(request, "Comentario anadido.")
                logger.info("Comentario creado en receta: %s", receta.titulo)
            except Exception as e:
                logger.error("Error al crear comentario: %s", str(e))
                messages.error(request, "Error al guardar el comentario.")
        else:
            messages.error(request, "Datos del comentario no validos.")
        return redirect("receta_detalle", pk=receta_pk)


# --- Exportacion ---

class ExportarView(View):
    def get(self, request):
        return render(request, "proyecto/exportar.html")

    def post(self, request):
        formato = request.POST.get("formato", "ambos")
        destino = "exportado"
        try:
            if formato == "csv":
                ExportService.exportar_csv(destino)
                messages.success(request, "Datos exportados a CSV correctamente.")
            elif formato == "xlsx":
                ExportService.exportar_xlsx(destino)
                messages.success(request, "Datos exportados a XLSX correctamente.")
            else:
                ExportService.exportar_todo(destino)
                messages.success(request, "Datos exportados a CSV y XLSX correctamente.")
            logger.info("Exportacion completada: formato=%s", formato)
        except Exception as e:
            logger.error("Error en exportacion: %s", str(e))
            messages.error(request, f"Error al exportar: {str(e)}")
        return redirect("exportar")
