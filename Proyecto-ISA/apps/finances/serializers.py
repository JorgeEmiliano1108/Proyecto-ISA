"""
Serializers for Finances app - Bonos integration.
"""
from rest_framework import serializers
import uuid


class CalculoLogroRequestSerializer(serializers.Serializer):
    """Schema para request de cálculo de logro individual."""
    evaluacion_id = serializers.UUIDField()
    calificacion_global = serializers.FloatField(min_value=1.0, max_value=5.0)


class CalculoLogroBatchItemSerializer(serializers.Serializer):
    """Schema para item individual en request batch."""
    evaluacion_id = serializers.UUIDField()
    calificacion_global = serializers.FloatField(min_value=1.0, max_value=5.0)


class CalculoLogroBatchRequestSerializer(serializers.Serializer):
    """Schema para request de cálculo batch."""
    registros = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        max_length=10000
    )


class CalculoLogroResponseSerializer(serializers.Serializer):
    """Schema de respuesta para cálculo de logro."""
    evaluacion_id = serializers.UUIDField()
    calificacion_global = serializers.FloatField()
    porcentaje_logro = serializers.FloatField()
    fecha_calculo = serializers.DateTimeField()


class CalculoLogroBatchRequestSerializer(serializers.Serializer):
    """Schema para request de cálculo batch."""
    registros = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        max_length=10000
    )


class CalculoLogroReportResponseSerializer(serializers.Serializer):
    """Schema de respuesta para reporte de logros."""
    periodo_id = serializers.IntegerField()
    total_evaluaciones = serializers.IntegerField()
    calculos = serializers.ListField(child=serializers.DictField())


class CalculoLogroListItemSerializer(serializers.Serializer):
    """Schema para item de lista de cálculos de logro."""
    id = serializers.UUIDField()
    evaluacion_id = serializers.UUIDField()
    calificacion_global = serializers.FloatField()
    porcentaje_logro = serializers.FloatField()
    fecha_calculo = serializers.DateTimeField()
    calculado_por = serializers.CharField()


class PaginatedCalculosResponseSerializer(serializers.Serializer):
    """Schema de respuesta paginada para listado de cálculos."""
    total = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    items = serializers.ListField(child=serializers.DictField())


class CalculosListQueryParamsSerializer(serializers.Serializer):
    """Query parameters para listar cálculos con filtros."""
    evaluacion_id = serializers.UUIDField(required=False)
    calculado_por = serializers.CharField(required=False)
    fecha_desde = serializers.DateTimeField(required=False)
    fecha_hasta = serializers.DateTimeField(required=False)
    page = serializers.IntegerField(default=1, min_value=1)
    page_size = serializers.IntegerField(default=20, min_value=1, max_value=100)


class BonoProgramaSerializer(serializers.Serializer):
    """Serializer para programa de bono."""
    id = serializers.UUIDField(read_only=True)
    nombre = serializers.CharField(max_length=255)
    descripcion = serializers.CharField(allow_blank=True)
    tipo_calculo = serializers.ChoiceField(choices=['porcentaje_salario', 'monto_fijo'])
    valor = serializers.DecimalField(max_digits=10, decimal_places=2)
    presupuesto_limite = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    fecha_inicio = serializers.DateField()
    fecha_fin = serializers.DateField()
    estado = serializers.ChoiceField(choices=['activo', 'planeado', 'finalizado'], default='activo')
    fecha_creacion = serializers.DateTimeField(read_only=True)
    fecha_actualizacion = serializers.DateTimeField(read_only=True)


class BonoEmpleadoSerializer(serializers.Serializer):
    """Serializer para asignación de empleado a programa de bono."""
    id = serializers.UUIDField(read_only=True)
    programa = serializers.UUIDField()
    empleado_id = serializers.UUIDField()
    salario_base = serializers.DecimalField(max_digits=12, decimal_places=2)
    objetivo = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    estado = serializers.ChoiceField(choices=['en_progreso', 'completado', 'pendiente'], default='pendiente')
    fecha_asignacion = serializers.DateTimeField(read_only=True)
    fecha_actualizacion = serializers.DateTimeField(read_only=True)


class BonoPagoSerializer(serializers.Serializer):
    """Serializer para historial de pagos."""
    id = serializers.UUIDField(read_only=True)
    empleado_id = serializers.UUIDField()
    programa_id = serializers.UUIDField()
    monto = serializers.DecimalField(max_digits=12, decimal_places=2)
    periodo = serializers.CharField(max_length=50)
    fecha_pago = serializers.DateField()
    estado = serializers.ChoiceField(choices=['pendiente', 'pagado', 'rechazado'])


class BonoMetasVinculadasSerializer(serializers.Serializer):
    """Serializer para metas vinculadas al bono."""
    id = serializers.UUIDField(read_only=True)
    programa_id = serializers.UUIDField()
    titulo = serializers.CharField(max_length=255)
    meta = serializers.CharField(max_length=100)
    actual = serializers.CharField(max_length=100)
    icono = serializers.CharField(max_length=10, required=False)
    fecha_creacion = serializers.DateTimeField(read_only=True)