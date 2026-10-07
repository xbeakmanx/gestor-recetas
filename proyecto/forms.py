from django import forms
from .models import Receta, Categoria, Ingrediente, Comentario, RecetaIngrediente


class RecetaForm(forms.ModelForm):
    class Meta:
        model = Receta
        fields = [
            "titulo", "descripcion", "instrucciones",
            "categoria", "tiempo_preparacion", "dificultad",
        ]
        widgets = {
            "titulo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombre de la receta",
            }),
            "descripcion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Breve descripcion de la receta",
            }),
            "instrucciones": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 6,
                "placeholder": "Pasos para preparar la receta",
            }),
            "categoria": forms.Select(attrs={"class": "form-select"}),
            "tiempo_preparacion": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
                "placeholder": "Minutos",
            }),
            "dificultad": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_titulo(self):
        titulo = self.cleaned_data["titulo"].strip()
        if len(titulo) < 3:
            raise forms.ValidationError("El titulo debe tener al menos 3 caracteres.")
        return titulo

    def clean_tiempo_preparacion(self):
        tiempo = self.cleaned_data["tiempo_preparacion"]
        if tiempo <= 0:
            raise forms.ValidationError("El tiempo debe ser mayor a 0.")
        if tiempo > 1440:
            raise forms.ValidationError("El tiempo no puede superar las 24 horas (1440 minutos).")
        return tiempo


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nombre", "descripcion"]
        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombre de la categoria",
            }),
            "descripcion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Descripcion opcional",
            }),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        if len(nombre) < 2:
            raise forms.ValidationError("El nombre debe tener al menos 2 caracteres.")
        return nombre


class IngredienteForm(forms.ModelForm):
    class Meta:
        model = Ingrediente
        fields = ["nombre", "unidad_base"]
        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombre del ingrediente",
            }),
            "unidad_base": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej: g, ml, unidad, cucharada",
            }),
        }


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ["contenido", "puntuacion"]
        widgets = {
            "contenido": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Escribe tu comentario",
            }),
            "puntuacion": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
                "max": 5,
            }),
        }

    def clean_puntuacion(self):
        puntuacion = self.cleaned_data["puntuacion"]
        if puntuacion < 1 or puntuacion > 5:
            raise forms.ValidationError("La puntuacion debe estar entre 1 y 5.")
        return puntuacion


class RecetaIngredienteForm(forms.ModelForm):
    class Meta:
        model = RecetaIngrediente
        fields = ["ingrediente", "cantidad", "unidad", "opcional"]
        widgets = {
            "ingrediente": forms.Select(attrs={"class": "form-select"}),
            "cantidad": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0.01,
                "step": 0.01,
            }),
            "unidad": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej: g, ml, unidad",
            }),
            "opcional": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


RecetaIngredienteFormSet = forms.inlineformset_factory(
    Receta,
    RecetaIngrediente,
    form=RecetaIngredienteForm,
    extra=3,
    can_delete=True,
)
