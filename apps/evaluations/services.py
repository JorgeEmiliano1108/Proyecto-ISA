"""
Servicios de Evaluaciones - Lógica de Negocio.
Cumple con OWASP SbD - Defense in Depth:
- Separar Capa de servicios de la capa de presentación (views)
- Centraliza la lógica de la máquina de estados
"""
from django.db import transaction
from django.utils import timezone
from apps.evaluations.models import Evaluaciones, CompetenciasDetalle, Objetivos
from apps.audit.models import HistorialEstados


class EvaluationService:
    """
    Servicio que maneja la lógica de negocio de las evaluaciones.
    
    Máquina de Estados:
    DRAFT -> SUBMITTED -> PENDING_APPROVAL -> APPROVED -> CLOSED
    
    Este servicio cumple con OWASP SbD:
    - Domain 1: Core Secure Design Principles
    - Domain 4: Reliability & Resilience (manejo de errores)
    """
    
    ESTADO_DRAFT = 'DRAFT'
    ESTADO_SUBMITTED = 'SUBMITTED'
    ESTADO_PENDING_APPROVAL = 'PENDING_APPROVAL'
    ESTADO_APPROVED = 'APPROVED'
    ESTADO_CLOSED = 'CLOSED'
    ESTADO_REJECTED = 'REJECTED'
    
    @staticmethod
    @transaction.atomic
    def submit_evaluation(evaluacion, usuario):
        """
        Transición: DRAFT -> SUBMITTED
        
        El empleado envía su evaluación para revisión.
        
        Validaciones:
        - La evaluación debe estar en estado DRAFT
        - El usuario debe ser el evaluado
        - Todas las competencias deben estar calificadas
        
        Args:
            evaluacion: Instancia de Evaluaciones
            usuario: Usuario que realiza la acción
            
        Returns:
            evaluacion: Instancia actualizada
            
        Raises:
            ValueError: Si no cumple las validaciones
        """
        if evaluacion.estado != EvaluationService.ESTADO_DRAFT:
            raise ValueError(
                f"Solo se puede enviar una evaluación en estado DRAFT. "
                f"Estado actual: {evaluacion.estado}"
            )
        
        if evaluacion.evaluado_id != usuario.id:
            raise ValueError("Solo el empleado puede enviar su propia evaluación.")
        
        competencias = CompetenciasDetalle.objects.filter(evaluacion=evaluacion)
        if competencias.count() == 0:
            raise ValueError("Debe agregar al menos una competencia evaluada.")
        
        for comp in competencias:
            if comp.calificacion is None:
                raise ValueError(f"La competencia '{comp.competencia.nombre}' no tiene calificación.")
        
        estado_anterior = evaluacion.estado
        evaluacion.estado = EvaluationService.ESTADO_SUBMITTED
        evaluacion.fecha_actualizacion = timezone.now()
        evaluacion.save()
        
        HistorialEstados.objects.create(
            evaluacion=evaluacion,
            estado_anterior=estado_anterior,
            estado_nuevo=EvaluationService.ESTADO_SUBMITTED,
            usuario=usuario,
            comentario='Evaluación enviada por el empleado'
        )
        
        return evaluacion
    
    @staticmethod
    @transaction.atomic
    def approve_evaluation(evaluacion, usuario, comentario=None):
        """
        Transición: SUBMITTED/PENDING_APPROVAL -> APPROVED
        
        El coordinador/gerente aprueba la evaluación.
        
        Args:
            evaluacion: Instancia de Evaluaciones
            usuario: Usuario que aprueba
            comentario: Comentario opcional
            
        Returns:
            evaluacion: Instancia actualizada
        """
        if evaluacion.estado not in [
            EvaluationService.ESTADO_SUBMITTED,
            EvaluationService.ESTADO_PENDING_APPROVAL
        ]:
            raise ValueError(
                f"No se puede aprobar una evaluación en estado {evaluacion.estado}"
            )
        
        estado_anterior = evaluacion.estado
        evaluacion.estado = EvaluationService.ESTADO_APPROVED
        evaluacion.fecha_actualizacion = timezone.now()
        evaluacion.save()
        
        HistorialEstados.objects.create(
            evaluacion=evaluacion,
            estado_anterior=estado_anterior,
            estado_nuevo=EvaluationService.ESTADO_APPROVED,
            usuario=usuario,
            comentario=comentario or 'Evaluación aprobada'
        )
        
        return evaluacion
    
    @staticmethod
    @transaction.atomic
    def reject_evaluation(evaluacion, usuario, comentario):
        """
        Transición: PENDING_APPROVAL -> REJECTED (regresa a DRAFT)
        
        El gerente/revisor rechaza la evaluación.
        IMPORTANTE: Un rechazo regresa la evaluación a estado DRAFT.
        
        Args:
            evaluacion: Instancia de Evaluaciones
            usuario: Usuario que rechaza
            comentario: Comentario obligatorio (requerido por negocio)
            
        Returns:
            evaluacion: Instancia actualizada
        """
        if evaluacion.estado != EvaluationService.ESTADO_PENDING_APPROVAL:
            raise ValueError(
                f"Solo se puede rechazar una evaluación en estado PENDING_APPROVAL. "
                f"Estado actual: {evaluacion.estado}"
            )
        
        if not comentario or len(comentario.strip()) < 10:
            raise ValueError(
                "El comentario de rechazo es obligatorio y debe tener al menos 10 caracteres."
            )
        
        estado_anterior = evaluacion.estado
        evaluacion.estado = EvaluationService.ESTADO_DRAFT
        evaluacion.fecha_actualizacion = timezone.now()
        evaluacion.save()
        
        HistorialEstados.objects.create(
            evaluacion=evaluacion,
            estado_anterior=estado_anterior,
            estado_nuevo=EvaluationService.ESTADO_DRAFT,
            usuario=usuario,
            comentario=f"RECHAZADA: {comentario}"
        )
        
        return evaluacion
    
    @staticmethod
    def get_transitions(estado_actual):
        """
        Retorna las transiciones disponibles desde el estado actual.
        
        Args:
            estado_actual: Estado actual de la evaluación
            
        Returns:
            list: Lista de estados destino disponibles
        """
        transitions = {
            'DRAFT': ['SUBMITTED'],
            'SUBMITTED': ['PENDING_APPROVAL'],
            'PENDING_APPROVAL': ['APPROVED', 'DRAFT'],
            'APPROVED': ['CLOSED'],
            'CLOSED': [],
            'REJECTED': []
        }
        return transitions.get(estado_actual, [])
