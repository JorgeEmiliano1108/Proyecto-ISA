"""
Vistas para Evaluaciones.
Cumple con OWASP SbD - Defense in Depth:
- Separa la capa de presentación (views) de la lógica de negocio (services)
- Usa permisos a nivel de objeto (permissions.py)
- Optimiza consultas con select_related y prefetch_related
"""
from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.evaluations.models import Evaluaciones, CompetenciasDetalle, Objetivos
from apps.evaluations.serializers import (
    EvaluacionSerializer,
    EvaluacionCreateSerializer,
    EvaluacionUpdateSerializer,
    EvaluacionTransitionSerializer,
    CompetenciaDetalleSerializer,
    ObjetivoSerializer
)
from apps.evaluations.permissions import IsManagerOrContraloriaOrSelf
from apps.evaluations.services import EvaluationService


class EvaluacionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Evaluaciones.
    
    Endpoints:
    - GET /evaluations/ - Listar evaluaciones
    - POST /evaluations/ - Crear evaluación
    - GET /evaluations/{id}/ - Ver evaluación
    - PUT/PATCH /evaluations/{id}/ - Actualizar evaluación
    - DELETE /evaluations/{id}/ - Eliminar evaluación
    - POST /evaluations/{id}/submit/ - Enviar evaluación
    - POST /evaluations/{id}/approve/ - Aprobar evaluación
    - POST /evaluations/{id}/reject/ - Rechazar evaluación
    """
    permission_classes = [IsAuthenticated, IsManagerOrContraloriaOrSelf]
    
    def get_serializer_class(self):
        """Selecciona el serializer según el método HTTP."""
        if self.action == 'create':
            return EvaluacionCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return EvaluacionUpdateSerializer
        return EvaluacionSerializer
    
    def get_queryset(self):
        """
        Optimiza consultas para evitar problema N+1.
        Filtra por permisos: admin/contraloria ve todo,
        los demás solo ven evaluaciones donde son evaluado,
        evaluador, o manager de evaluado/evaluador.
        """
        qs = Evaluaciones.objects.select_related(
            'evaluado',
            'evaluado__rol',
            'evaluado__departamento',
            'evaluador',
            'evaluador__rol',
            'periodo'
        ).prefetch_related(
            'competenciasdetalle_set',
            'competenciasdetalle_set__competencia',
            'objetivos_set',
            'historialestados_set',
            'historialestados_set__usuario'
        )

        user = self.request.user
        user_rol = getattr(user, 'rol', None)
        rol_nombre = getattr(user_rol, 'nombre', '').lower() if user_rol else ''

        if rol_nombre in ['administrador', 'contraloria']:
            return qs

        return qs.filter(
            models.Q(evaluado=user) |
            models.Q(evaluador=user) |
            models.Q(evaluado__manager=user) |
            models.Q(evaluador__manager=user)
        ).order_by('-fecha_creacion')
    
    # ============================================
    # ACCIONES DE TRANSICIÓN (State Machine)
    # ============================================
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def submit(self, request, pk=None):
        """
        Transición: DRAFT -> SUBMITTED
        
        Endpoint: POST /api/v1/evaluations/{id}/submit/
        
        El empleado envía su evaluación para revisión.
        """
        evaluacion = self.get_object()
        
        try:
            evaluacion = EvaluationService.submit_evaluation(
                evaluacion=evaluacion,
                usuario=request.user
            )
            serializer = EvaluacionSerializer(evaluacion)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def approve(self, request, pk=None):
        """
        Transición: SUBMITTED/PENDING_APPROVAL -> APPROVED
        
        Endpoint: POST /api/v1/evaluations/{id}/approve/
        
        El coordinador/gerente aprueba la evaluación.
        """
        evaluacion = self.get_object()
        serializer = EvaluacionTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            evaluacion = EvaluationService.approve_evaluation(
                evaluacion=evaluacion,
                usuario=request.user,
                comentario=serializer.validated_data.get('comentario')
            )
            result_serializer = EvaluacionSerializer(evaluacion)
            return Response(result_serializer.data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reject(self, request, pk=None):
        """
        Transición: PENDING_APPROVAL -> DRAFT (rechazada)
        
        Endpoint: POST /api/v1/evaluations/{id}/reject/
        
        El gerente/revisor rechaza la evaluación.
        IMPORTANTE: Requiere comentario obligatorio.
        """
        evaluacion = self.get_object()
        serializer = EvaluacionTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        comentario = serializer.validated_data.get('comentario', '')
        
        if not comentario or len(comentario.strip()) < 10:
            return Response(
                {'error': 'El comentario de rechazo es obligatorio y debe tener al menos 10 caracteres.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            evaluacion = EvaluationService.reject_evaluation(
                evaluacion=evaluacion,
                usuario=request.user,
                comentario=comentario
            )
            result_serializer = EvaluacionSerializer(evaluacion)
            return Response(result_serializer.data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        evaluacion = self.get_object()
        if evaluacion.estado != 'DRAFT':
            return Response(
                {'error': 'Solo se pueden eliminar evaluaciones en estado DRAFT.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def transitions(self, request):
        """
        Obtiene las transiciones disponibles según el estado.
        
        Endpoint: GET /api/v1/evaluations/transitions/?estado=DRAFT
        """
        estado = request.query_params.get('estado', 'DRAFT')
        transitions = EvaluationService.get_transitions(estado)
        return Response({'estado': estado, 'transiciones_disponibles': transitions})

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def logro(self, request, pk=None):
        """
        Obtiene el porcentaje de logro calculado para una evaluación.
        
        Endpoint: GET /api/v1/evaluations/{id}/logro/
        
        Retorna:
        - evaluacion_id
        - calificacion_global
        - porcentaje_logro (calculado por bonus_service)
        - fecha_calculo (si está disponible)
        """
        evaluacion = self.get_object()
        
        data = {
            'evaluacion_id': str(evaluacion.id),
            'estado': evaluacion.estado,
            'calificacion_global': evaluacion.calificacion_global,
            'porcentaje_logro': evaluacion.porcentaje_logro,
        }
        
        # Si tiene porcentaje_logro, significa que ya fue calculado
        if evaluacion.porcentaje_logro is not None:
            data['calculado'] = True
            data['mensaje'] = f'Porcentaje de logro: {evaluacion.porcentaje_logro}%'
        else:
            data['calculado'] = False
            if evaluacion.estado == 'APPROVED':
                data['mensaje'] = 'Evaluación aprobada pero porcentaje de logro no calculado aún'
            else:
                data['mensaje'] = 'La evaluación debe estar aprobada para calcular el logro'
        
        return Response(data, status=status.HTTP_200_OK)
