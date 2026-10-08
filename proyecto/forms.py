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
                "placeholder": "Breve descripción de la receta",
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["categoria"].empty_label = "Seleccionar categoría"

    def clean_titulo(self):
        titulo = self.cleaned_data["titulo"].strip()
        if len(titulo) < 3:
            raise forms.ValidationError("El título debe tener al menos 3 caracteres.")
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
                "placeholder": "Nombre de la categoría",
            }),
            "descripcion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Descripción opcional",
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
            raise forms.ValidationError("La puntuación debe estar entre 1 y 5.")
        return puntuacion


class RecetaIngredienteForm(forms.ModelForm):
    class Meta:
        model = RecetaIngrediente
        fields = ["ingrediente", "cantidad", "unidad", "opcional"]
        widgets = {
            "ingrediente": forms.Select(attrs={"class": "form-select form-select-sm"}),
            "cantidad": forms.NumberInput(attrs={
                "class": "form-control form-control-sm",
                "min": 0.01,
                "step": 0.01,
                "placeholder": "Cantidad",
            }),
            "unidad": forms.TextInput(attrs={
                "class": "form-control form-control-sm",
                "placeholder": "Ej: g, ml, unidad",
            }),
            "opcional": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["ingrediente"].empty_label = "Seleccionar"


RecetaIngredienteFormSet = forms.inlineformset_factory(
    Receta,
    RecetaIngrediente,
    form=RecetaIngredienteForm,
    extra=3,
    can_delete=True,
)


class RegistroForm(forms.Form):
    nombre = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Tu nombre completo",
        }),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "correo@ejemplo.com",
        }),
    )
    contrasena = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Mínimo 6 caracteres",
        }),
    )
    contrasena_confirmacion = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Repite la contraseña",
        }),
    )

    def clean_email(self):
        from .models import Usuario
        email = self.cleaned_data["email"]
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe un usuario con este correo.")
        return email

    def clean(self):
        cleaned = super().clean()
        contra = cleaned.get("contrasena")
        confirmacion = cleaned.get("contrasena_confirmacion")
        if contra and confirmacion and contra != confirmacion:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "correo@ejemplo.com",
        }),
    )
    contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Tu contraseña",
        }),
    )
