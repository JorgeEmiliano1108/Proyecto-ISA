"""Capa de Vistas - Transporte HTTP"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Count, Avg
from ..models import Employee, Evaluation, Bono, ApprovalRequest
from ..serializers import (
    EmployeeSerializer, 
    EvaluationSerializer, 
    BonoSerializer,
    ApprovalRequestSerializer
)


class EmployeeViewSet(viewsets.ModelViewSet):
    """ViewSet para Empleados"""
    queryset = Employee.objects.filter(is_active=True)
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Employee.objects.filter(is_active=True)


class EvaluationViewSet(viewsets.ModelViewSet):
    """ViewSet para Evaluaciones"""
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Datos para el dashboard"""
        total = Evaluation.objects.count()
        pending = Evaluation.objects.filter(status='pending').count()
        approved = Evaluation.objects.filter(status='approved').count()
        rejected = Evaluation.objects.filter(status='rejected').count()
        
        avg_score = Evaluation.objects.filter(
            status='approved'
        ).aggregate(Avg('performance_score'))
        
        return Response({
            'total_evaluations': total,
            'pending': pending,
            'approved': approved,
            'rejected': rejected,
            'average_score': avg_score.get('performance_score__avg', 0)
        })

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Enviar evaluación para aprobación"""
        evaluation = self.get_object()
        if evaluation.status != 'draft':
            return Response(
                {'error': 'Solo evaluaciones en borrador pueden ser enviadas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from .services.evaluation_service import EvaluationService
        result = EvaluationService.submit_evaluation(evaluation.id)
        return Response(result)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Aprobar evaluación"""
        evaluation = self.get_object()
        if evaluation.status != 'pending':
            return Response(
                {'error': 'La evaluación debe estar pendiente'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from .services.evaluation_service import EvaluationService
        result = EvaluationService.approve_evaluation(
            evaluation.id, 
            request.user
        )
        return Response(result)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Rechazar evaluación"""
        evaluation = self.get_object()
        if evaluation.status != 'pending':
            return Response(
                {'error': 'La evaluación debe estar pendiente'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from .services.evaluation_service import EvaluationService
        result = EvaluationService.reject_evaluation(
            evaluation.id,
            request.user,
            request.data.get('reason', '')
        )
        return Response(result)


class BonoViewSet(viewsets.ModelViewSet):
    """ViewSet para Bonos"""
    queryset = Bono.objects.all()
    serializer_class = BonoSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Bonos pendientes de aprobación"""
        bonos = Bono.objects.filter(status='pending')
        serializer = self.get_serializer(bonos, many=True)
        return Response(serializer.data)


class ApprovalRequestViewSet(viewsets.ModelViewSet):
    """ViewSet para Solicitudes de Aprobación"""
    queryset = ApprovalRequest.objects.all()
    serializer_class = ApprovalRequestSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Aprobar solicitud"""
        approval_request = self.get_object()
        
        if approval_request.request_type == 'evaluation':
            from .services.evaluation_service import EvaluationService
            result = EvaluationService.approve_evaluation(
                approval_request.object_id,
                request.user
            )
        elif approval_request.request_type == 'bono':
            from .services.bono_service import BonoService
            result = BonoService.approve_bono(
                approval_request.object_id,
                request.user
            )
        
        return Response(result)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Rechazar solicitud"""
        approval_request = self.get_object()
        approval_request.status = 'rejected'
        approval_request.save()
        
        return Response({'status': 'rejected'})