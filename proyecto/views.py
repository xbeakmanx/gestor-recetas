import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponse, Http404

import hashlib

from .models import Receta, Categoria, Ingrediente, Usuario, Comentario, RecetaIngrediente, Favorito
from .forms import (
    RecetaForm, CategoriaForm, IngredienteForm,
    ComentarioForm, RecetaIngredienteFormSet,
    RegistroForm, LoginForm,
)
from .services import RecetaService, ExportService

logger = logging.getLogger("proyecto")


#obtener_usuario():
#   usuario_id ← OBTENER "usuario_id" DE la sesión
#   SI usuario_id EXISTE:
#       usuario ← BUSCAR Usuario POR usuario_id
#       SI usuario EXISTE:
#           RETORNAR usuario
#   usuario ← OBTENER O CREAR usuario administrador por defecto
#   RETORNAR usuario
class UsuarioMixin:
    def get_usuario(self):
        usuario_id = self.request.session.get("usuario_id")
        if usuario_id:
            try:
                return Usuario.objects.get(pk=usuario_id)
            except Usuario.DoesNotExist:
                pass
        usuario, _ = Usuario.objects.get_or_create(
            email="admin@recetas.com",
            defaults={
                "nombre": "Administrador",
                "contrasena_hash": "no-auth",
            },
        )
        return usuario


#inicio(petición):
#   estadísticas ← RecetaService.estadísticas()
#   últimas_recetas ← OBTENER las 5 recetas más recientes con sus relaciones
#   RENDERIZAR plantilla "inicio.html" CON estadísticas Y últimas_recetas
class InicioView(View):
    def get(self, request):
        try:
            estadisticas = RecetaService.estadisticas()
            ultimas_recetas = Receta.objects.select_related(
                "usuario", "categoria"
            ).prefetch_related("imagenes")[:5]
        except Exception as e:
            logger.error("Error al cargar inicio: %s", str(e))
            estadisticas = {}
            ultimas_recetas = []
        return render(request, "proyecto/inicio.html", {
            "estadisticas": estadisticas,
            "ultimas_recetas": ultimas_recetas,
        })


#listar_recetas(filtros):
#   recetas ← OBTENER todas las recetas con sus relaciones
#   SI filtros.categoría EXISTE:
#       recetas ← FILTRAR recetas POR categoría
#   SI filtros.dificultad EXISTE:
#       recetas ← FILTRAR recetas POR dificultad
#   SI filtros.búsqueda EXISTE:
#       recetas ← FILTRAR recetas DONDE título O descripción CONTENGA el término
#   RETORNAR recetas paginadas (12 por página)
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
        usuario_id = self.request.session.get("usuario_id")
        if usuario_id:
            context["favoritas_ids"] = set(
                Favorito.objects.filter(usuario_id=usuario_id).values_list("receta_id", flat=True)
            )
        return context


#detalle_receta(pk):
#   receta ← RecetaService.obtener(pk) CON ingredientes, imágenes y comentarios
#   SI receta NO EXISTE:
#       ERROR 404
#   SI el usuario tiene sesión:
#       es_favorita ← VERIFICAR si existe Favorito(usuario, receta)
#   RENDERIZAR plantilla "receta_detalle.html" CON receta, ingredientes, formulario de comentario
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
        usuario_id = self.request.session.get("usuario_id")
        if usuario_id:
            context["es_favorita"] = Favorito.objects.filter(
                usuario_id=usuario_id, receta=self.object
            ).exists()
        return context


#crear_receta(datos_formulario, datos_ingredientes):
#   SI el usuario NO tiene sesión:
#       REDIRIGIR a login CON parámetro next = ruta actual
#   usuario ← OBTENER usuario actual de la sesión
#   SI el formulario de receta NO es válido:
#       MOSTRAR errores de validación
#       RETORNAR
#   SI el formset de ingredientes NO es válido:
#       MOSTRAR errores
#       RETORNAR
#   receta ← CREAR Receta con datos_formulario
#   receta.usuario ← usuario
#   GUARDAR receta
#   PARA CADA ingrediente EN datos_ingredientes:
#       CREAR RecetaIngrediente(receta, ingrediente, cantidad, unidad)
#   MOSTRAR mensaje "Receta creada correctamente"
#   REDIRIGIR a lista de recetas
class RecetaCreateView(UsuarioMixin, CreateView):
    model = Receta
    form_class = RecetaForm
    template_name = "proyecto/receta_form.html"
    success_url = reverse_lazy("receta_lista")

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("usuario_id"):
            return redirect(f"{reverse_lazy('login')}?next={request.path}")
        return super().dispatch(request, *args, **kwargs)

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
                messages.success(self.request, f"Receta «{self.object.titulo}» creada correctamente.")
                logger.info("Receta creada desde vista: %s", self.object.titulo)
                return redirect(self.success_url)
            else:
                return self.render_to_response(context)
        except Exception as e:
            logger.error("Error al crear receta: %s", str(e))
            messages.error(self.request, "Error al crear la receta. Inténtalo de nuevo.")
            return self.form_invalid(form)


#actualizar_receta(pk, datos_formulario, datos_ingredientes):
#   receta ← OBTENER Receta POR pk
#   SI el formulario NO es válido:
#       MOSTRAR errores
#       RETORNAR
#   SI el formset de ingredientes NO es válido:
#       MOSTRAR errores
#       RETORNAR
#   ACTUALIZAR receta CON datos_formulario
#   GUARDAR cambios en ingredientes
#   MOSTRAR mensaje "Receta actualizada"
#   REDIRIGIR a lista de recetas
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


#eliminar_receta(pk):
#   receta ← OBTENER Receta POR pk
#   CONFIRMAR eliminación con el usuario
#   ELIMINAR receta de la base de datos
#   MOSTRAR mensaje "Receta eliminada"
#   REDIRIGIR a lista de recetas
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


#listar_categorías():
#   categorías ← OBTENER todas las categorías
#   RENDERIZAR plantilla "categoria_lista.html" CON categorías
class CategoriaListView(ListView):
    model = Categoria
    template_name = "proyecto/categoria_lista.html"
    context_object_name = "categorias"


#crear_categoría(nombre, descripción):
#   SI el formulario NO es válido:
#       MOSTRAR errores
#       RETORNAR
#   categoría ← CREAR Categoría(nombre, descripción)
#   MOSTRAR mensaje "Categoría creada correctamente"
#   SI viene desde formulario de receta:
#       REDIRIGIR a crear receta
#   SINO:
#       REDIRIGIR a lista de categorías
class CategoriaCreateView(CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "proyecto/categoria_form.html"
    success_url = reverse_lazy("categoria_lista")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo_pagina"] = "Nueva Categoría"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Categoría creada correctamente.")
        response = super().form_valid(form)
        if self.request.GET.get("next") == "receta":
            return redirect("receta_crear")
        return response


#actualizar_categoría(pk, nombre, descripción):
#   categoría ← OBTENER Categoría POR pk
#   ACTUALIZAR categoría CON nuevos datos
#   MOSTRAR mensaje "Categoría actualizada"
#   REDIRIGIR a lista de categorías
class CategoriaUpdateView(UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "proyecto/categoria_form.html"
    success_url = reverse_lazy("categoria_lista")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo_pagina"] = "Editar Categoría"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Categoría actualizada correctamente.")
        return super().form_valid(form)


#eliminar_categoría(pk):
#   categoría ← OBTENER Categoría POR pk
#   ELIMINAR categoría
#   MOSTRAR mensaje "Categoría eliminada"
#   REDIRIGIR a lista de categorías
class CategoriaDeleteView(DeleteView):
    model = Categoria
    template_name = "proyecto/categoria_confirmar_eliminar.html"
    success_url = reverse_lazy("categoria_lista")
    context_object_name = "categoria"

    def form_valid(self, form):
        messages.success(self.request, "Categoría eliminada.")
        return super().form_valid(form)


#listar_ingredientes():
#   ingredientes ← OBTENER todos los ingredientes
#   RENDERIZAR plantilla "ingrediente_lista.html" CON ingredientes
class IngredienteListView(ListView):
    model = Ingrediente
    template_name = "proyecto/ingrediente_lista.html"
    context_object_name = "ingredientes"


#crear_ingrediente(nombre, unidad_base):
#   SI el formulario NO es válido:
#       MOSTRAR errores
#       RETORNAR
#   ingrediente ← CREAR Ingrediente(nombre, unidad_base)
#   MOSTRAR mensaje "Ingrediente creado correctamente"
#   REDIRIGIR a lista de ingredientes
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


#actualizar_ingrediente(pk, nombre, unidad_base):
#   ingrediente ← OBTENER Ingrediente POR pk
#   ACTUALIZAR ingrediente CON nuevos datos
#   MOSTRAR mensaje "Ingrediente actualizado"
#   REDIRIGIR a lista de ingredientes
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


#eliminar_ingrediente(pk):
#   ingrediente ← OBTENER Ingrediente POR pk
#   ELIMINAR ingrediente
#   MOSTRAR mensaje "Ingrediente eliminado"
#   REDIRIGIR a lista de ingredientes
class IngredienteDeleteView(DeleteView):
    model = Ingrediente
    template_name = "proyecto/ingrediente_confirmar_eliminar.html"
    success_url = reverse_lazy("ingrediente_lista")
    context_object_name = "ingrediente"

    def form_valid(self, form):
        messages.success(self.request, "Ingrediente eliminado.")
        return super().form_valid(form)


#añadir_comentario(receta_pk, contenido, puntuación):
#   receta ← BUSCAR Receta POR receta_pk
#   SI NO EXISTE:
#       ERROR 404
#   SI el formulario es válido:
#       comentario ← CREAR Comentario
#       comentario.usuario ← usuario actual de la sesión
#       comentario.receta ← receta
#       GUARDAR comentario
#       MOSTRAR "Comentario añadido"
#   SINO:
#       MOSTRAR "Datos del comentario no válidos"
#   REDIRIGIR al detalle de la receta
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
                messages.success(request, "Comentario añadido.")
                logger.info("Comentario creado en receta: %s", receta.titulo)
            except Exception as e:
                logger.error("Error al crear comentario: %s", str(e))
                messages.error(request, "Error al guardar el comentario.")
        else:
            messages.error(request, "Datos del comentario no válidos.")
        return redirect("receta_detalle", pk=receta_pk)


#exportar_datos(formato):
#   SI formato = "csv":
#       PARA CADA modelo EN [Usuarios, Categorías, Ingredientes, ...]:
#           dataframe ← modelo.todos().convertir_a_dataframe()
#           GUARDAR dataframe COMO archivo CSV
#   SINO SI formato = "xlsx":
#       CREAR archivo Excel
#       PARA CADA modelo EN [Usuarios, Categorías, Ingredientes, ...]:
#           dataframe ← modelo.todos().convertir_a_dataframe()
#           ESCRIBIR dataframe COMO hoja del Excel
#   SINO:
#       EJECUTAR exportar_csv()
#       EJECUTAR exportar_xlsx()
#   MOSTRAR mensaje de éxito
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


#registrar_usuario(nombre, email, contraseña):
#   SI el formulario NO es válido:
#       MOSTRAR errores de validación
#       RETORNAR
#   hash ← SHA256(contraseña)
#   usuario ← CREAR Usuario(nombre, email, hash)
#   GUARDAR usuario.id EN sesión
#   GUARDAR usuario.nombre EN sesión
#   MOSTRAR mensaje "Bienvenido/a"
#   REDIRIGIR a página de inicio
class RegistroView(View):
    def get(self, request):
        form = RegistroForm()
        return render(request, "proyecto/registro.html", {"form": form})

    def post(self, request):
        form = RegistroForm(request.POST)
        if form.is_valid():
            try:
                contrasena_hash = hashlib.sha256(
                    form.cleaned_data["contrasena"].encode()
                ).hexdigest()
                usuario = Usuario.objects.create(
                    nombre=form.cleaned_data["nombre"],
                    email=form.cleaned_data["email"],
                    contrasena_hash=contrasena_hash,
                )
                request.session["usuario_id"] = usuario.pk
                request.session["usuario_nombre"] = usuario.nombre
                messages.success(request, f"Bienvenido/a, {usuario.nombre}.")
                logger.info("Usuario registrado: %s", usuario.email)
                return redirect("inicio")
            except Exception as e:
                logger.error("Error en registro: %s", str(e))
                messages.error(request, "Error al crear la cuenta.")
        return render(request, "proyecto/registro.html", {"form": form})


#iniciar_sesion(email, contraseña):
#   hash ← SHA256(contraseña)
#   usuario ← BUSCAR en Usuarios DONDE email = email
#   SI usuario NO EXISTE:
#       MOSTRAR error "Correo o contraseña incorrectos"
#       RETORNAR
#   SI usuario.contraseña_hash ≠ hash:
#       MOSTRAR error "Contraseña incorrecta"
#       RETORNAR
#   GUARDAR usuario.id EN sesión
#   GUARDAR usuario.nombre EN sesión
#   SI hay URL de redirección (next):
#       REDIRIGIR a esa URL
#   SINO:
#       REDIRIGIR a página de inicio
class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, "proyecto/login.html", {"form": form, "next": request.GET.get("next", "")})

    def post(self, request):
        form = LoginForm(request.POST)
        next_url = request.POST.get("next", "")
        if form.is_valid():
            email = form.cleaned_data["email"]
            contrasena_hash = hashlib.sha256(
                form.cleaned_data["contrasena"].encode()
            ).hexdigest()
            try:
                usuario = Usuario.objects.get(email=email)
                if usuario.contrasena_hash == contrasena_hash:
                    request.session["usuario_id"] = usuario.pk
                    request.session["usuario_nombre"] = usuario.nombre
                    messages.success(request, f"Hola, {usuario.nombre}.")
                    logger.info("Login exitoso: %s", email)
                    if next_url and next_url.startswith("/"):
                        return redirect(next_url)
                    return redirect("inicio")
                else:
                    logger.warning("Contraseña incorrecta para: %s", email)
                    return render(request, "proyecto/login.html", {
                        "form": form,
                        "error": "Correo o contraseña incorrectos.",
                        "next": next_url,
                    })
            except Usuario.DoesNotExist:
                logger.warning("Intento de login con email no registrado: %s", email)
                return render(request, "proyecto/login.html", {
                    "form": form,
                    "error": "Correo o contraseña incorrectos.",
                    "next": next_url,
                })
        return render(request, "proyecto/login.html", {"form": form, "next": next_url})


#cerrar_sesion():
#   ELIMINAR todos los datos de la sesión
#   MOSTRAR mensaje "Sesión cerrada"
#   REDIRIGIR a página de inicio
class LogoutView(View):
    def get(self, request):
        request.session.flush()
        messages.success(request, "Sesión cerrada.")
        return redirect("inicio")


#alternar_favorito(usuario, receta_pk):
#   receta ← BUSCAR Receta POR receta_pk
#   SI NO EXISTE:
#       ERROR 404
#   favorito ← BUSCAR Favorito DONDE usuario Y receta
#   SI favorito EXISTE:
#       ELIMINAR favorito
#       MOSTRAR "Eliminada de favoritos"
#   SINO:
#       CREAR Favorito(usuario, receta)
#       MOSTRAR "Añadida a favoritos"
#   REDIRIGIR a página anterior
class ToggleFavoritoView(UsuarioMixin, View):
    def post(self, request, receta_pk):
        receta = get_object_or_404(Receta, pk=receta_pk)
        usuario = self.get_usuario()
        favorito = Favorito.objects.filter(usuario=usuario, receta=receta)
        if favorito.exists():
            favorito.delete()
            messages.success(request, f"«{receta.titulo}» eliminada de favoritos.")
        else:
            Favorito.objects.create(usuario=usuario, receta=receta)
            messages.success(request, f"«{receta.titulo}» añadida a favoritos.")
        next_url = request.POST.get("next", "receta_lista")
        if next_url.startswith("/"):
            return redirect(next_url)
        return redirect("receta_detalle", pk=receta_pk)


#listar_favoritas():
#   usuario ← OBTENER usuario actual de la sesión
#   recetas ← OBTENER recetas DONDE exista Favorito(usuario, receta)
#   RENDERIZAR plantilla "favoritas.html" CON recetas
class FavoritasView(UsuarioMixin, ListView):
    template_name = "proyecto/favoritas.html"
    context_object_name = "recetas"

    def get_queryset(self):
        usuario = self.get_usuario()
        return Receta.objects.filter(
            guardado_por__usuario=usuario
        ).select_related("usuario", "categoria")
