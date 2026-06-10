import uuid
from django.db import models
from django.conf import settings


class BonoPrograma(models.Model):
    """Modelo para programas de bonos/bonificaciones."""
    
    TIPO_CALCULO_CHOICES = [
        ('porcentaje_salario', 'Porcentaje Salario Base'),
        ('monto_fijo', 'Monto Fijo'),
    ]
    
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('planeado', 'Planeado'),
        ('finalizado', 'Finalizado'),
        ('pausado', 'Pausado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    tipo_calculo = models.CharField(max_length=30, choices=[
        ('porcentaje_salario', 'Porcentaje Salario Base'),
        ('monto_fijo', 'Monto Fijo'),
    ])
    valor = models.DecimalField(max_digits=10, decimal_places=2, help_text="Porcentaje (ej: 15.00) o monto fijo")
    presupuesto_limite = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.CharField(max_length=20, choices=[
        ('activo', 'Activo'),
        ('planeado', 'Planeado'),
        ('finalizado', 'Finalizado'),
        ('pausado', 'Pausado'),
    ], default='activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bonos_creados'
    )
    
    class Meta:
        db_table = 'bonos_programas'
        ordering = ['-fecha_creacion']
        verbose_name = 'Programa de Bono'
        verbose_name_plural = 'Programas de Bonos'
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_calculo_display()})"


class BonoEmpleado(models.Model):
    """Asignación de empleado a programa de bono."""
    
    ESTADO_CHOICES = [
        ('en_progreso', 'En Progreso'),
        ('completado', 'Completado'),
        ('pendiente', 'Pendiente'),
        ('cancelado', 'Cancelado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    programa = models.ForeignKey(
        'BonoPrograma',
        on_delete=models.CASCADE,
        related_name='empleados_asignados'
    )
    empleado = models.ForeignKey(
        'users.Usuarios',
        on_delete=models.CASCADE,
        related_name='bonos_asignados'
    )
    evaluador = models.ForeignKey(
        'users.Usuarios',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bonos_evaluados'
    )
    salario_base = models.DecimalField(max_digits=12, decimal_places=2)
    objetivo = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=[
        ('en_progreso', 'En Progreso'),
        ('completado', 'Completado'),
        ('pendiente', 'Pendiente'),
        ('cancelado', 'Cancelado'),
    ], default='pendiente')
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bonos_empleados'
        unique_together = ['programa', 'empleado']
        verbose_name = 'Empleado en Bono'
        verbose_name_plural = 'Empleados en Bonos'
    
    def __str__(self):
        return f"{self.empleado} - {self.programa.nombre}"


class BonoPago(models.Model):
    """Historial de pagos de bonos."""
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('rechazado', 'Rechazado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empleado = models.ForeignKey(
        'users.Usuarios',
        on_delete=models.CASCADE,
        related_name='bonos_pagos'
    )
    programa = models.ForeignKey(
        'BonoPrograma',
        on_delete=models.CASCADE,
        related_name='pagos'
    )
    empleado_asignado = models.ForeignKey(
        'BonoEmpleado',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pagos'
    )
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    periodo = models.CharField(max_length=50, help_text="Ej: Q1 2024, Q2 2024, etc.")
    fecha_pago = models.DateField()
    estado = models.CharField(max_length=20, choices=[
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('rechazado', 'Rechazado'),
    ], default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bonos_pagos'
        ordering = ['-fecha_pago']
        verbose_name = 'Pago de Bono'
        verbose_name_plural = 'Pagos de Bonos'
    
    def __str__(self):
        return f"{self.empleado} - {self.periodo} - {self.monto}"


class BonoMetasVinculadas(models.Model):
    """Metas/KPIs vinculados a un programa de bono."""
    
    ICONO_CHOICES = [
        ('🖥️', '🖥️ Servidor/Infraestructura'),
        ('📜', '📜 Certificación'),
        ('🤝', '🤝 Equipo/Feedback'),
        ('📈', '📈 Ventas/Metas'),
        ('🎯', '🎯 Objetivo General'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    programa = models.ForeignKey(
        'BonoPrograma',
        on_delete=models.CASCADE,
        related_name='metas_vinculadas'
    )
    titulo = models.CharField(max_length=255)
    meta = models.CharField(max_length=100, help_text="Ej: 99.9%, 1, 4.5/5")
    actual = models.CharField(max_length=100, help_text="Valor actual alcanzado")
    icono = models.CharField(max_length=10, choices=ICONO_CHOICES, default='🎯')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'bonos_metas_vinculadas'
        verbose_name = 'Meta Vinculada'
        verbose_name_plural = 'Metas Vinculadas'
    
    def __str__(self):
        return f"{self.programa.nombre} - {self.titulo}"