"""Capa de Servicios - Lógica de Negocio para Bonos"""
from django.utils import timezone
from django.db import transaction
from ..models import Bono, Evaluation


class BonoService:
    """Servicio para Bonos - Capa de Escritura"""

    @staticmethod
    @transaction.atomic
    def create_bono(data: dict, user) -> dict:
        """Crear nuevo bono"""
        evaluation = None
        if 'evaluation_id' in data:
            evaluation = Evaluation.objects.filter(id=data['evaluation_id']).first()

        bono = Bono.objects.create(
            employee_id=data['employee_id'],
            evaluation=evaluation,
            amount=data['amount'],
            period=data['period'],
            reason=data.get('reason', ''),
            status='pending'
        )

        return {
            'id': bono.id,
            'status': bono.status,
            'amount': float(bono.amount),
            'message': 'Bono creado exitosamente'
        }

    @staticmethod
    @transaction.atomic
    def approve_bono(bono_id: int, user) -> dict:
        """Aprobar bono"""
        try:
            bono = Bono.objects.get(id=bono_id)
            
            if bono.status != 'pending':
                raise ValueError('El bono debe estar pendiente')

            bono.status = 'approved'
            bono.approved_by = user
            bono.approved_at = timezone.now()
            bono.save()

            return {
                'id': bono.id,
                'status': bono.status,
                'message': f'Bono aprobado por {user.get_full_name()}'
            }
        except Bono.DoesNotExist:
            raise ValueError('Bono no encontrado')

    @staticmethod
    @transaction.atomic
    def reject_bono(bono_id: int, user, reason: str = '') -> dict:
        """Rechazar bono"""
        try:
            bono = Bono.objects.get(id=bono_id)
            
            if bono.status != 'pending':
                raise ValueError('El bono debe estar pendiente')

            bono.status = 'rejected'
            bono.save()

            return {
                'id': bono.id,
                'status': bono.status,
                'message': f'Bono rechazado por {user.get_full_name()}'
            }
        except Bono.DoesNotExist:
            raise ValueError('Bono no encontrado')

    @staticmethod
    @transaction.atomic
    def mark_as_paid(bono_id: int) -> dict:
        """Marcar bono como pagado"""
        try:
            bono = Bono.objects.get(id=bono_id)
            
            if bono.status != 'approved':
                raise ValueError('Solo bonos aprobados pueden ser marcados como pagados')

            bono.status = 'paid'
            bono.save()

            return {
                'id': bono.id,
                'status': bono.status,
                'message': 'Bono marcado como pagado'
            }
        except Bono.DoesNotExist:
            raise ValueError('Bono no encontrado')