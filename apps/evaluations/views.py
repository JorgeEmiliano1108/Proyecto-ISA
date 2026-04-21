"""
Vistas para Evaluaciones.
Cumple con OWASP SbD - Defense in Depth:
- Separa la capa de presentación (views) de la lógica de negocio (services)
- Usa permisos a nivel de objeto (permissions.py)
- Optimiza consultas con select_related y prefetch_related
"""
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
        Usa select_related y prefetch_related.
        """
        return Evaluaciones.objects.select_related(
            'evaluado',
            'evaluado__rol',
            'evaluado__departamento',
            'evaluador',
            'evaluador__rol',
            'periodo'
        ).prefetch_related(
            'competencias_detalle_set',
            'competencias_detalle_set__competencia',
            'objetivos_set',
            'historialestado_set',
            'historialestado_set__usuario'
        )
    
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
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def transitions(self, request):
        """
        Obtiene las transiciones disponibles según el estado.
        
        Endpoint: GET /api/v1/evaluations/transitions/?estado=DRAFT
        """
        estado = request.query_params.get('estado', 'DRAFT')
        transitions = EvaluationService.get_transitions(estado)
        return Response({'estado': estado, 'transiciones_disponibles': transitions})
