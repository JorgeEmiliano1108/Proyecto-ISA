from django.contrib import admin
from django import forms
from django.contrib.auth.hashers import make_password
from .models import Usuarios


class UsuariosAdminForm(forms.ModelForm):
    class Meta:
        model = Usuarios
        fields = '__all__'
        widgets = {
            'password': forms.PasswordInput(render_value=True),
        }


@admin.register(Usuarios)
class UsuariosAdmin(admin.ModelAdmin):
    form = UsuariosAdminForm
    list_display = ('username', 'nombre_completo', 'puesto', 'rol', 'departamento')
    search_fields = ('username', 'nombre_completo')
    list_filter = ('rol', 'departamento')

    def save_model(self, request, obj, form, change):
        if obj.password and not obj.password.startswith('pbkdf2_'):
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)
