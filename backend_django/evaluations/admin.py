from django.contrib import admin
from .models import Employee, Evaluation, Bono, ApprovalRequest


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'user', 'department', 'position', 'is_active']
    search_fields = ['employee_id', 'user__first_name', 'user__last_name']
    list_filter = ['department', 'is_active']


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee', 'period', 'status', 'performance_score', 'created_at']
    search_fields = ['employee__employee_id', 'period']
    list_filter = ['status', 'period']


@admin.register(Bono)
class BonoAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee', 'amount', 'period', 'status', 'created_at']
    search_fields = ['employee__employee_id', 'period']
    list_filter = ['status', 'period']


@admin.register(ApprovalRequest)
class ApprovalRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'request_type', 'requested_by', 'status', 'created_at']
    list_filter = ['request_type', 'status']