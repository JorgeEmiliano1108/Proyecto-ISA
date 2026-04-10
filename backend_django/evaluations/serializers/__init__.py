from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Employee, Evaluation, Bono, ApprovalRequest


class UserSerializer(serializers.ModelSerializer):
    """Serializer para usuario de Django"""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'is_active']
        read_only_fields = ['id']

    def get_full_name(self, obj):
        return obj.get_full_name()


class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer para Empleado"""
    user = UserSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            'id', 'user', 'full_name', 'employee_id', 
            'department', 'position', 'hire_date', 
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_full_name(self, obj):
        return obj.user.get_full_name()


class EvaluationSerializer(serializers.ModelSerializer):
    """Serializer para Evaluación"""
    employee_name = serializers.SerializerMethodField()
    evaluator_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()
    total_score = serializers.SerializerMethodField()

    class Meta:
        model = Evaluation
        fields = [
            'id', 'employee', 'employee_name', 'evaluator', 'evaluator_name',
            'period', 'performance_score', 'punctuality_score', 
            'teamwork_score', 'initiative_score', 'total_score',
            'strengths', 'improvements', 'general_comments',
            'status', 'created_at', 'updated_at', 
            'submitted_at', 'approved_at', 'approved_by', 'approved_by_name'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'submitted_at', 'approved_at']

    def get_employee_name(self, obj):
        return obj.employee.user.get_full_name()

    def get_evaluator_name(self, obj):
        return obj.evaluator.get_full_name() if obj.evaluator else None

    def get_approved_by_name(self, obj):
        return obj.approved_by.get_full_name() if obj.approved_by else None

    def get_total_score(self, obj):
        return obj.calculate_total_score()


class BonoSerializer(serializers.ModelSerializer):
    """Serializer para Bono"""
    employee_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Bono
        fields = [
            'id', 'employee', 'employee_name', 'evaluation',
            'amount', 'period', 'reason', 'status',
            'approved_by', 'approved_by_name', 'approved_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'approved_at']

    def get_employee_name(self, obj):
        return obj.employee.user.get_full_name()

    def get_approved_by_name(self, obj):
        return obj.approved_by.get_full_name() if obj.approved_by else None


class ApprovalRequestSerializer(serializers.ModelSerializer):
    """Serializer para Solicitud de Aprobación"""
    requested_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ApprovalRequest
        fields = [
            'id', 'request_type', 'content_type', 'object_id',
            'requested_by', 'requested_by_name', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_requested_by_name(self, obj):
        return obj.requested_by.get_full_name()