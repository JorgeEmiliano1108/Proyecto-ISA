"""
Servicios de Evaluaciones - Lógica de Negocio.
Cumple con OWASP SbD - Defense in Depth:
- Separar Capa de servicios de la capa de presentación (views)
- Centraliza la lógica de la máquina de estados
"""
import logging
import requests
import uuid
from datetime import datetime, timedelta
from django.db import transaction, models
from django.utils import timezone
from django.conf import settings
from apps.evaluations.models import Evaluaciones, CompetenciasDetalle, Objetivos
from apps.audit.models import HistorialEstados
from apps.evaluations.event_publisher import publish_event
from cryptography.hazmat.primitives.serialization import load_pem_private_key

logger = logging.getLogger(__name__)


class EvaluationService:
    """
    Servicio que maneja la lógica de negocio de las evaluaciones.
    
    Máquina de Estados:
    DRAFT -> SUBMITTED -> PENDING_APPROVAL -> APPROVED -> CLOSED
    
    Este servicio cumple con OWASP SbD:
    - Domain 1: Core Secure Design Principles
    - Domain 4: Reliability & Resilience (manejo de errores)
    """
    
    FULL_ACCESS_ROLES = ['administrador', 'contraloria']

    ESTADO_DRAFT = 'DRAFT'
    ESTADO_SUBMITTED = 'SUBMITTED'
    ESTADO_PENDING_APPROVAL = 'PENDING_APPROVAL'
    ESTADO_APPROVED = 'APPROVED'
    ESTADO_CLOSED = 'CLOSED'
    ESTADO_REJECTED = 'REJECTED'
    
    # ============================================
    # CONEXIÓN A MICROSERVICIOS (JWT RS256)
    # ============================================
    @staticmethod
    def _generar_token_jwt_interno() -> str:
        """
        Genera un token JWT firmado con RS256 usando la clave privada de Django.
        El token incluye claims para identificación del servicio.
        """
        import jwt
        from datetime import datetime, timedelta
        from cryptography.hazmat.primitives.serialization import load_pem_private_key
        
        private_key_str = settings.JWT_PRIVATE_KEY
        if not private_key_str:
            logger.error("[BONUS-SERVICE] JWT_PRIVATE_KEY no configurado en settings")
            return None
            
        payload = {
            "sub": "django-backend",
            "service": "django-evaluations",
            "roles": ["internal-service", "bonus-calculator"],
            "exp": datetime.utcnow() + timedelta(minutes=10),
            "iat": datetime.utcnow(),
            "jti": str(uuid.uuid4()),
        }
        
        try:
            # Cargar la clave privada usando cryptography (maneja correctamente el formato PEM)
            private_key = load_pem_private_key(
                settings.JWT_PRIVATE_KEY.encode('utf-8'),
                password=None
            )
            
            token = jwt.encode(payload, private_key, algorithm="RS256")
            return token
        except Exception as e:
            logger.error(f"[BONUS-SERVICE] Error generando JWT: {e}")
            return None
    
    @staticmethod
    def solicitar_calculo_logro(evaluacion_id: str, calificacion_global: float) -> dict:
        """
        Envía una petición HTTP POST al microservicio de bonos 
        para calcular el porcentaje de logro de forma síncrona.
        
        Args:
            evaluacion_id: UUID de la evaluación
            calificacion_global: Calificación entre 1.0 y 5.0
            
        Returns:
            dict: Resultado del cálculo con porcentaje_logro, o None si falla
        """
        url = f"{settings.BONUS_SERVICE_URL}/api/v1/bonus/calculate"
        
        payload = {
            "evaluacion_id": evaluacion_id,
            "calificacion_global": float(calificacion_global)
        }
        
        # Generar token JWT RS256 firmado con clave privada de Django
        token = EvaluationService._generar_token_jwt_interno()
        if not token:
            logger.error(f"[BONUS-SERVICE] No se pudo generar token JWT")
            return None
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        try:
            logger.info(f"[BONUS-SERVICE] Enviando cálculo para evaluación {evaluacion_id}...")
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            resultado = response.json()
            porcentaje = resultado.get('porcentaje_logro')
            logger.info(f"[BONUS-SERVICE] ✓ Éxito: evaluación {evaluacion_id} -> {porcentaje}%")
            
            return {
                "evaluacion_id": evaluacion_id,
                "porcentaje_logro": porcentaje,
                "calificacion_global": calificacion_global
            }
            
        except requests.exceptions.Timeout:
            logger.error(f"[BONUS-SERVICE] ✗ Timeout: No respondió en 10s para evaluación {evaluacion_id}")
            return None
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"[BONUS-SERVICE] ✗ Conexión fallida: {e}")
            return None
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"[BONUS-SERVICE] ✗ HTTP Error {e.response.status_code}: {e.response.text}")
            return None
            
        except Exception as e:
            logger.error(f"[BONUS-SERVICE] ✗ Error inesperado: {type(e).__name__} - {e}")
            return None

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

        publish_event('EVALUATION_SUBMITTED', evaluacion.id, estado_anterior, EvaluationService.ESTADO_SUBMITTED, usuario.id)
        
        return evaluacion
    
    @staticmethod
    @transaction.atomic
    def approve_evaluation(evaluacion, usuario, comentario=None):
        """
        Aprobación de 2 niveles con validación jerárquica.
        
        Nivel 1 (SUBMITTED -> PENDING_APPROVAL): solo el evaluador.
        Nivel 2 (PENDING_APPROVAL -> APPROVED): solo el manager del evaluador.
        FULL_ACCESS_ROLES (Administrador/Contraloría) bypassan la jerarquía.
        
        Args:
            evaluacion: Instancia de Evaluaciones
            usuario: Usuario que aprueba
            comentario: Comentario opcional
            
        Returns:
            evaluacion: Instancia actualizada
        """
        user_rol = getattr(usuario, 'rol', None)
        rol_nombre = getattr(user_rol, 'nombre', '').lower() if user_rol else ''
        is_full_access = rol_nombre in EvaluationService.FULL_ACCESS_ROLES

        if evaluacion.estado == EvaluationService.ESTADO_SUBMITTED:
            if not is_full_access and evaluacion.evaluador_id != usuario.id:
                raise ValueError(
                    "Solo el evaluador puede aprobar en este nivel."
                )

            estado_anterior = evaluacion.estado
            evaluacion.estado = EvaluationService.ESTADO_PENDING_APPROVAL
            evaluacion.fecha_actualizacion = timezone.now()
            evaluacion.save()

            HistorialEstados.objects.create(
                evaluacion=evaluacion,
                estado_anterior=estado_anterior,
                estado_nuevo=EvaluationService.ESTADO_PENDING_APPROVAL,
                usuario=usuario,
                comentario=comentario or 'Aprobación nivel 1'
            )

            publish_event('EVALUATION_APPROVED_N1', evaluacion.id, estado_anterior, EvaluationService.ESTADO_PENDING_APPROVAL, usuario.id, comentario)

        elif evaluacion.estado == EvaluationService.ESTADO_PENDING_APPROVAL:
            if not is_full_access:
                manager = getattr(evaluacion.evaluador, 'manager', None)
                if not manager or manager.id != usuario.id:
                    raise ValueError(
                        "Solo el manager del evaluador puede aprobar en este nivel."
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
                comentario=comentario or 'Aprobación nivel 2'
            )

            publish_event('EVALUATION_APPROVED_N2', evaluacion.id, estado_anterior, EvaluationService.ESTADO_APPROVED, usuario.id, comentario)

            # ============================================
            # DISPARAR CÁLCULO DE LOGRO AL BONUS SERVICE
            # ============================================
            if evaluacion.estado == EvaluationService.ESTADO_APPROVED:
                try:
                    competencias = CompetenciasDetalle.objects.filter(evaluacion=evaluacion)
                    if competencias.exists():
                        calificacion_promedio = competencias.aggregate(
                            promedio=models.Avg('calificacion')
                        )['promedio']
                        
                        if calificacion_promedio:
                            resultado_bono = EvaluationService.solicitar_calculo_logro(
                                evaluacion_id=str(evaluacion.id),
                                calificacion_global=round(calificacion_promedio, 2)
                            )
                            
                            if resultado_bono:
                                # Guardar porcentaje_logro en la evaluación
                                evaluacion.porcentaje_logro = resultado_bono['porcentaje_logro']
                                evaluacion.save(update_fields=['porcentaje_logro'])
                                
                                logger.info(
                                    f"[BONUS-SERVICE] Evaluación {evaluacion.id} aprobada. "
                                    f"Calificación: {calificacion_promedio:.2f} -> Logro: {resultado_bono['porcentaje_logro']}%"
                                )
                            else:
                                logger.warning(
                                    f"[BONUS-SERVICE] Evaluación {evaluacion.id} aprobada pero no se pudo calcular el logro."
                                )
                except Exception as e:
                    logger.error(f"[BONUS-SERVICE] Error al intentar calcular logro tras aprobación: {e}")

        else:
            raise ValueError(
                f"No se puede aprobar una evaluación en estado {evaluacion.estado}"
            )

        return evaluacion
    
    @staticmethod
    @transaction.atomic
    def reject_evaluation(evaluacion, usuario, comentario):
        """
        Transición: PENDING_APPROVAL -> DRAFT (rechazada)
        
        Solo el manager del evaluador puede rechazar.
        FULL_ACCESS_ROLES bypassan la jerarquía.
        El comentario de rechazo es obligatorio (mín. 10 caracteres).
        
        Args:
            evaluacion: Instancia de Evaluaciones
            usuario: Usuario que rechaza
            comentario: Comentario obligatorio
            
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

        user_rol = getattr(usuario, 'rol', None)
        rol_nombre = getattr(user_rol, 'nombre', '').lower() if user_rol else ''
        is_full_access = rol_nombre in EvaluationService.FULL_ACCESS_ROLES

        if not is_full_access:
            manager = getattr(evaluacion.evaluador, 'manager', None)
            if not manager or manager.id != usuario.id:
                raise ValueError(
                    "Solo el manager del evaluador puede rechazar la evaluación."
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

        publish_event('EVALUATION_REJECTED', evaluacion.id, estado_anterior, EvaluationService.ESTADO_DRAFT, usuario.id, comentario)

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
