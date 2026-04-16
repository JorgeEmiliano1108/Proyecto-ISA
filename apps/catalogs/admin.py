from django.contrib import admin
from .models import CatRoles, CatDepartamentos

@admin.register(CatRoles)
class CatRolesAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nivel_aprobacion', 'activo')

@admin.register(CatDepartamentos)
class CatDepartamentosAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')