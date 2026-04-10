from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Employee(models.Model):
    """Modelo de Empleado"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    hire_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employees'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.employee_id}"


class Evaluation(models.Model):
    """Modelo de Evaluación de Desempeño"""
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('submitted', 'Enviada'),
        ('pending', 'Pendiente de Aprobación'),
        ('approved', 'Aprobada'),
        ('rejected', 'Rechazada'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='evaluations')
    evaluator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='evaluations_given')
    period = models.CharField(max_length=20)  # Ej: "2024-Q1", "2024-01"
    
    # Métricas de evaluación
    performance_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    punctuality_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    teamwork_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    initiative_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Comments
    strengths = models.TextField(blank=True)
    improvements = models.TextField(blank=True)
    general_comments = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='evaluations_approved')

    class Meta:
        db_table = 'evaluations'
        ordering = ['-created_at']
        unique_together = ['employee', 'period']

    def __str__(self):
        return f"Evaluación {self.employee.employee_id} - {self.period}"

    def calculate_total_score(self):
        scores = [self.performance_score, self.punctuality_score, self.teamwork_score, self.initiative_score]
        valid_scores = [s for s in scores if s is not None]
        if valid_scores:
            return sum(valid_scores) / len(valid_scores)
        return None


class Bono(models.Model):
    """Modelo de Bono de Desempeño"""
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
        ('paid', 'Pagado'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='bonos')
    evaluation = models.OneToOneField(Evaluation, on_delete=models.SET_NULL, null=True, blank=True, related_name='bono')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    period = models.CharField(max_length=20)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='bonos_approved')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bonos'
        ordering = ['-created_at']

    def __str__(self):
        return f"Bono {self.employee.employee_id} - ${self.amount}"


class ApprovalRequest(models.Model):
    """Modelo de Solicitud de Aprobación"""
    TYPE_CHOICES = [
        ('evaluation', 'Evaluación'),
        ('bono', 'Bono'),
        ('user', 'Usuario'),
    ]

    TYPE_CHOICES = [
        ('evaluation', 'Evaluación'),
        ('bono', 'Bono'),
        ('user', 'Usuario'),
    ]

    request_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = models.GenericForeignKey('content_type', 'object_id')
    
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approval_requests')
    status = models.CharField(max_length=20, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'approval_requests'
        ordering = ['-created_at']

    def __str__(self):
        return f"Aprobación {self.request_type} - {self.pk}"