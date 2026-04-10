"""Capa de Selectors - Consultas Optimizadas (CQRS-lite)"""
from django.db.models import Count, Avg, Sum, Q, F
from django.db.models.functions import Coalesce
from datetime import datetime, timedelta
from ..models import Employee, Evaluation, Bono


class EvaluationSelector:
    """Selector para Evaluaciones - Capa de Lectura"""

    @staticmethod
    def get_all_evaluations(filters: dict = None):
        """Obtener todas las evaluaciones con filtros"""
        queryset = Evaluation.objects.select_related('employee', 'employee__user', 'evaluator')
        
        if filters:
            if filters.get('status'):
                queryset = queryset.filter(status=filters['status'])
            if filters.get('period'):
                queryset = queryset.filter(period=filters['period'])
            if filters.get('employee_id'):
                queryset = queryset.filter(employee_id=filters['employee_id'])
        
        return queryset.order_by('-created_at')

    @staticmethod
    def get_evaluation_by_id(evaluation_id: int):
        """Obtener evaluación por ID"""
        return Evaluation.objects.select_related(
            'employee',
            'employee__user',
            'evaluator',
            'approved_by'
        ).prefetch_related('bono_set').get(id=evaluation_id)

    @staticmethod
    def get_pending_evaluations():
        """Obtener evaluaciones pendientes de aprobación"""
        return Evaluation.objects.filter(
            status__in=['submitted', 'pending']
        ).select_related('employee', 'employee__user', 'evaluator')

    @staticmethod
    def get_employee_evaluations(employee_id: int):
        """Obtener evaluaciones de un empleado"""
        return Evaluation.objects.filter(
            employee_id=employee_id
        ).order_by('-period')

    @staticmethod
    def get_evaluations_by_period(period: str):
        """Obtener evaluaciones de un período específico"""
        return Evaluation.objects.filter(
            period=period
        ).select_related('employee', 'employee__user')

    @staticmethod
    def get_dashboard_stats():
        """Estadísticas para el dashboard"""
        total = Evaluation.objects.count()
        pending = Evaluation.objects.filter(status__in=['submitted', 'pending']).count()
        approved = Evaluation.objects.filter(status='approved').count()
        rejected = Evaluation.objects.filter(status='rejected').count()
        
        avg_score = Evaluation.objects.filter(
            status='approved'
        ).aggregate(avg=Coalesce(Avg('performance_score'), 0))
        
        return {
            'total': total,
            'pending': pending,
            'approved': approved,
            'rejected': rejected,
            'average_score': round(avg_score['avg'], 2)
        }

    @staticmethod
    def get_top_performers(limit: int = 10):
        """Obtener mejores desempeños"""
        return Evaluation.objects.filter(
            status='approved',
            performance_score__isnull=False
        ).select_related('employee', 'employee__user').order_by('-performance_score')[:limit]


class BonoSelector:
    """Selector para Bonos - Capa de Lectura"""

    @staticmethod
    def get_all_bonos(filters: dict = None):
        """Obtener todos los bonos con filtros"""
        queryset = Bono.objects.select_related('employee', 'employee__user', 'approved_by')
        
        if filters:
            if filters.get('status'):
                queryset = queryset.filter(status=filters['status'])
            if filters.get('period'):
                queryset = queryset.filter(period=filters['period'])
            if filters.get('employee_id'):
                queryset = queryset.filter(employee_id=filters['employee_id'])
        
        return queryset.order_by('-created_at')

    @staticmethod
    def get_bono_by_id(bono_id: int):
        """Obtener bono por ID"""
        return Bono.objects.select_related(
            'employee',
            'employee__user',
            'evaluation',
            'approved_by'
        ).get(id=bono_id)

    @staticmethod
    def get_pending_bonos():
        """Obtener bonos pendientes de aprobación"""
        return Bono.objects.filter(
            status='pending'
        ).select_related('employee', 'employee__user')

    @staticmethod
    def get_bonos_by_employee(employee_id: int):
        """Obtener bonos de un empleado"""
        return Bono.objects.filter(
            employee_id=employee_id
        ).order_by('-period')

    @staticmethod
    def get_total_bonos_paid(period: str = None):
        """Total de bonos pagados"""
        queryset = Bono.objects.filter(status='paid')
        
        if period:
            queryset = queryset.filter(period=period)
        
        total = queryset.aggregate(total=Coalesce(Sum('amount'), 0))
        return float(total['total'])

    @staticmethod
    def get_bonos_summary():
        """Resumen de bonos"""
        return Bono.objects.values('status').annotate(count=Count('id'))


class EmployeeSelector:
    """Selector para Empleados - Capa de Lectura"""

    @staticmethod
    def get_all_employees(filters: dict = None):
        """Obtener todos los empleados"""
        queryset = Employee.objects.select_related('user').filter(is_active=True)
        
        if filters:
            if filters.get('department'):
                queryset = queryset.filter(department=filters['department'])
            if filters.get('position'):
                queryset = queryset.filter(position__icontains=filters['position'])
        
        return queryset.order_by('user__first_name')

    @staticmethod
    def get_employee_by_id(employee_id: int):
        """Obtener empleado por ID"""
        return Employee.objects.select_related('user').get(id=employee_id)

    @staticmethod
    def get_employee_by_employee_id(employee_id: str):
        """Obtener empleado por código de empleado"""
        return Employee.objects.select_related('user').get(employee_id=employee_id)

    @staticmethod
    def get_employees_by_department(department: str):
        """Obtener empleados por departamento"""
        return Employee.objects.filter(
            department=department,
            is_active=True
        ).select_related('user')

    @staticmethod
    def get_departments():
        """Obtener lista de departamentos"""
        return Employee.objects.filter(
            is_active=True
        ).values_list('department', flat=True).distinct()