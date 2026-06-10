"""
Serializers para Evaluaciones.
Cumple con OWASP SbD - Secure-by-Design:
- Estado protegido (read_only) - solo services.py puede modificar
- Serializers anidados para relaciones
- Trazabilidad integrada
"""
from django.utils import timezone
from rest_framework import serializers
from apps.evaluations.models import Evaluaciones, CompetenciasDetalle, Objetivos
from apps.audit.models import HistorialEstados


# ============================================
# SERIALIZERS ANIDADOS (NESTED)
# ============================================

class CompetenciaDetalleSerializer(serializers.ModelSerializer):
    """
    Serializer para competencias detalle.
    Anidado en EvaluacionSerializer.
    """
    competencia_nombre = serializers.CharField(source='competencia.nombre', read_only=True)
    
    class Meta:
        model = CompetenciasDetalle
        fields = [
            'id',
            'competencia',
            'competencia_nombre',
            'calificacion',
            'comentario'
        ]


class ObjetivoSerializer(serializers.ModelSerializer):
    """
    Serializer para objetivos.
    Anidado en EvaluacionSerializer.
    """
    class Meta:
        model = Objetivos
        fields = ['id', 'descripcion']


class HistorialEstadoSerializer(serializers.ModelSerializer):
    """
    Serializer para historial de estados (trazabilidad).
    Anidado en EvaluacionSerializer para cumplir con LFPDPPP.
    """
    usuario_nombre = serializers.CharField(source='usuario.nombre_completo', read_only=True)
    
    class Meta:
        model = HistorialEstados
        fields = [
            'id',
            'estado_anterior',
            'estado_nuevo',
            'usuario_nombre',
            'comentario',
            'fecha'
        ]


# ============================================
# SERIALIZERS DE LECTURA (GET)
# ============================================

class EvaluacionSerializer(serializers.ModelSerializer):
    """
    Serializer de LECTURA para Evaluaciones.
    
    Incluye:
    - Datos del evaluado y evaluador (anidados)
    - Lista de competencias detalle (anidada)
    - Lista de objetivos (anidada)
    - Historial de cambios de estado (trazabilidad)
    
    Este serializer cumple con OWASP SbD:
    - Proporciona información completa en una sola petición
    - Trazabilidad para auditoría (LFPDPPP)
    """
    # Campos anidados del evaluado
    evaluado_nombre = serializers.CharField(source='evaluado.nombre_completo', read_only=True)
    evaluado_puesto = serializers.CharField(source='evaluado.puesto', read_only=True)
    
    # Campos anidados del evaluador
    evaluador_nombre = serializers.CharField(source='evaluador.nombre_completo', read_only=True)
    
    # Campos anidados del periodo
    periodo_nombre = serializers.CharField(source='periodo.nombre', read_only=True)
    
    # Serializers anidados
    competencias = CompetenciaDetalleSerializer(source='competenciasdetalle_set', many=True, read_only=True)
    objetivos = ObjetivoSerializer(many=True, read_only=True)
    historial = HistorialEstadoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Evaluaciones
        fields = [
            # Campos principales
            'id',
            'estado',
            'periodo',
            'periodo_nombre',
            'evaluado',
            'evaluado_nombre',
            'evaluado_puesto',
            'evaluador',
            'evaluador_nombre',
            
            # Datos de la evaluación
            'logros_previos',
            'comentarios_evaluador',
            'comentarios_evaluado',
            'calificacion_global',
            'porcentaje_logro',
            
            # Fechas
            'fecha_creacion',
            'fecha_actualizacion',
            'fecha_ultimo_recordatorio',
            
            # Serializers anidados
            'competencias',
            'objetivos',
            'historial'
        ]
        read_only_fields = fields


# ============================================
# SERIALIZERS DE ESCRITURA (POST/PUT)
# ============================================

class EvaluacionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer de ESCRITURA para crear Evaluaciones.
    
    CRITICAL SECURITY:
    - El campo 'estado' es read_only=True
    - Los cambios de estado solo se manejan via EvaluationService
    - Ningún endpoint REST puede modificar el estado directamente
    """
    class Meta:
        model = Evaluaciones
        fields = [
            'evaluado',
            'evaluador',
            'periodo',
            'logros_previos',
            'comentarios_evaluado',
        ]
    
    def create(self, validated_data):
        validated_data['estado'] = 'DRAFT'
        return super().create(validated_data)


class EvaluacionUpdateSerializer(serializers.ModelSerializer):
    competencias = serializers.ListField(child=serializers.DictField(), required=False, write_only=True)

    class Meta:
        model = Evaluaciones
        fields = [
            'logros_previos',
            'comentarios_evaluador',
            'comentarios_evaluado',
            'calificacion_global',
            'competencias',
        ]

    def update(self, instance, validated_data):
        competencias_data = validated_data.pop('competencias', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.fecha_actualizacion = timezone.now()
        instance.save()

        if competencias_data:
            from apps.evaluations.models import CompetenciasDetalle
            existing = {cd.competencia_id: cd for cd in CompetenciasDetalle.objects.filter(evaluacion=instance)}
            for item in competencias_data:
                comp_id = item.get('competencia')
                calif = item.get('calificacion')
                if comp_id and calif is not None:
                    if comp_id in existing:
                        cd = existing[comp_id]
                        cd.calificacion = calif
                        cd.save()
                    else:
                        CompetenciasDetalle.objects.create(
                            evaluacion=instance,
                            competencia_id=comp_id,
                            calificacion=calif,
                            comentario=''
                        )

        return instance


# ============================================
# SERIALIZERS PARA TRANSICIONES (State Machine)
# ============================================

class EvaluacionTransitionSerializer(serializers.Serializer):
    """
    Serializer para validar las transiciones de estado.
    Usado en los endpoints de submit/approve/reject.
    """
    comentario = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, attrs):
        return attrs
