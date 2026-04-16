from django.contrib import admin
from django import forms
from django.contrib.auth.hashers import make_password
from .models import Usuarios

# 1. Creamos un formulario personalizado para ocultar la contraseña con asteriscos
class UsuariosAdminForm(forms.ModelForm):
    class Meta:
        model = Usuarios
        fields = '__all__'
        widgets = {
            'password_hash': forms.PasswordInput(render_value=True),
        }

@admin.register(Usuarios)
class UsuariosAdmin(admin.ModelAdmin):
    form = UsuariosAdminForm # Le asignamos el formulario con asteriscos
    list_display = ('username', 'nombres', 'apellido_paterno', 'puesto', 'rol', 'departamento')
    search_fields = ('username', 'nombres', 'apellido_paterno')
    list_filter = ('rol', 'departamento')

    # 2. Magia: Encriptar automáticamente la contraseña al guardar en el panel
    def save_model(self, request, obj, form, change):
        # Si la contraseña no está encriptada todavía (no empieza con la firma de Django)
        if obj.password_hash and not obj.password_hash.startswith('pbkdf2_'):
            obj.password_hash = make_password(obj.password_hash)
        
        super().save_model(request, obj, form, change)