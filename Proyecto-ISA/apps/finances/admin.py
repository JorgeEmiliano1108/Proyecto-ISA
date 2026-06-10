"""
Admin configuration for Finances app.
"""
from django.contrib import admin
from .models import BonoPrograma, BonoEmpleado, BonoPago, BonoMetasVinculadas


@admin.register(BonoPrograma)
class BonoProgramaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo_calculo', 'valor', 'estado', 'fecha_inicio', 'fecha_fin', 'fecha_creacion']
    list_filter = ['estado', 'tipo_calculo', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    list_display_links = ['nombre']
    ordering = ['-fecha_creacion']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'tipo_calculo', 'valor', 'presupuesto_limite')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin')
        }),
        ('Estado', {
            'fields': ('estado',)
        }),
        ('Auditoría', {
            'fields': ('creado_por', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )


@admin.register(BonoEmpleado)
class BonoEmpleadoAdmin(admin.ModelAdmin):
    list_display = ['empleado', 'programa', 'salario_base', 'estado', 'fecha_asignacion']
    list_filter = ['estado', 'programa', 'fecha_asignacion']
    search_fields = ['empleado__username', 'empleado__nombre_completo', 'programa__nombre']
    readonly_fields = ['fecha_asignacion', 'fecha_actualizacion']
    list_display_links = ['empleado']
    ordering = ['-fecha_asignacion']
    
    fieldsets = (
        ('Asignación', {
            'fields': ('programa', 'empleado', 'evaluador')
        }),
        ('Detalles Económicos', {
            'fields': ('salario_base', 'objetivo')
        }),
        ('Estado', {
            'fields': ('estado',)
        }),
        ('Auditoría', {
            'fields': ('fecha_asignacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )


@admin.register(BonoPago)
class BonoPagoAdmin(admin.ModelAdmin):
    list_display = ['empleado', 'programa', 'periodo', 'monto', 'estado', 'fecha_pago']
    list_filter = ['estado', 'programa', 'periodo']
    search_fields = ['empleado__username', 'empleado__nombre_completo', 'programa__nombre']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    list_display_links = ['empleado']
    ordering = ['-fecha_pago']
    
    fieldsets = (
        ('Información del Pago', {
            'fields': ('empleado', 'programa', 'empleado_asignado', 'periodo', 'monto')
        }),
        ('Estado y Fecha', {
            'fields': ('estado', 'fecha_pago')
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )


@admin.register(BonoMetasVinculadas)
class BonoMetasVinculadasAdmin(admin.ModelAdmin):
    list_display = ['programa', 'titulo', 'meta', 'actual', 'icono', 'fecha_creacion']
    list_filter = ['programa', 'icono', 'fecha_creacion']
    search_fields = ['titulo', 'programa__nombre']
    readonly_fields = ['fecha_creacion']
    ordering = ['-fecha_creacion']