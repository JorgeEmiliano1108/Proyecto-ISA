"""Capa de Servicios - Lógica de Negocio"""
from django.utils import timezone
from django.db import transaction
from ..models import Evaluation


class EvaluationService:
    """Servicio para Evaluaciones - Capa de Escritura"""

    @staticmethod
    @transaction.atomic
    def create_evaluation(data: dict, user) -> dict:
        """Crear nueva evaluación"""
        evaluation = Evaluation.objects.create(
            employee_id=data['employee_id'],
            evaluator=user,
            period=data['period'],
            performance_score=data.get('performance_score'),
            punctuality_score=data.get('punctuality_score'),
            teamwork_score=data.get('teamwork_score'),
            initiative_score=data.get('initiative_score'),
            strengths=data.get('strengths', ''),
            improvements=data.get('improvements', ''),
            general_comments=data.get('general_comments', ''),
            status='draft'
        )
        return {
            'id': evaluation.id,
            'status': evaluation.status,
            'message': 'Evaluación creada exitosamente'
        }

    @staticmethod
    @transaction.atomic
    def submit_evaluation(evaluation_id: int) -> dict:
        """Enviar evaluación para aprobación"""
        try:
            evaluation = Evaluation.objects.get(id=evaluation_id)
            
            if evaluation.status != 'draft':
                raise ValueError('Solo evaluaciones en borrador pueden ser enviadas')

            total_score = evaluation.calculate_total_score()
            if total_score is None:
                raise ValueError('La evaluación debe tener al menos una puntuación')

            evaluation.status = 'submitted'
            evaluation.submitted_at = timezone.now()
            evaluation.save()

            return {
                'id': evaluation.id,
                'status': evaluation.status,
                'total_score': float(total_score),
                'message': 'Evaluación enviada para aprobación'
            }
        except Evaluation.DoesNotExist:
            raise ValueError('Evaluación no encontrada')

    @staticmethod
    @transaction.atomic
    def approve_evaluation(evaluation_id: int, user) -> dict:
        """Aprobar evaluación"""
        try:
            evaluation = Evaluation.objects.get(id=evaluation_id)
            
            if evaluation.status not in ['submitted', 'pending']:
                raise ValueError('La evaluación debe estar enviada o pendiente')

            evaluation.status = 'approved'
            evaluation.approved_at = timezone.now()
            evaluation.approved_by = user
            evaluation.save()

            return {
                'id': evaluation.id,
                'status': evaluation.status,
                'message': f'Evaluación aprobada por {user.get_full_name()}'
            }
        except Evaluation.DoesNotExist:
            raise ValueError('Evaluación no encontrada')

    @staticmethod
    @transaction.atomic
    def reject_evaluation(evaluation_id: int, user, reason: str = '') -> dict:
        """Rechazar evaluación"""
        try:
            evaluation = Evaluation.objects.get(id=evaluation_id)
            
            if evaluation.status not in ['submitted', 'pending']:
                raise ValueError('La evaluación debe estar enviada o pendiente')

            evaluation.status = 'rejected'
            evaluation.general_comments = f"{evaluation.general_comments}\n\nRazón de rechazo: {reason}".strip()
            evaluation.save()

            return {
                'id': evaluation.id,
                'status': evaluation.status,
                'message': f'Evaluación rechazada por {user.get_full_name()}'
            }
        except Evaluation.DoesNotExist:
            raise ValueError('Evaluación no encontrada')

    @staticmethod
    @transaction.atomic
    def calculate_bonus(evaluation_id: int) -> dict:
        """Calcular posible bono basado en evaluación"""
        try:
            evaluation = Evaluation.objects.get(id=evaluation_id)
            
            if evaluation.status != 'approved':
                raise ValueError('Solo evaluaciones aprobadas pueden generar bono')

            total_score = evaluation.calculate_total_score()
            
            bonus_amount = 0
            if total_score:
                if total_score >= 90:
                    bonus_amount = 1000
                elif total_score >= 80:
                    bonus_amount = 750
                elif total_score >= 70:
                    bonus_amount = 500
                elif total_score >= 60:
                    bonus_amount = 250

            return {
                'evaluation_id': evaluation.id,
                'total_score': float(total_score),
                'recommended_bonus': bonus_amount,
                'message': f'Bono recomendado: ${bonus_amount}'
            }
        except Evaluation.DoesNotExist:
            raise ValueError('Evaluación no encontrada')