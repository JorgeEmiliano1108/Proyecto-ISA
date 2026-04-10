from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.views import (
    EmployeeViewSet,
    EvaluationViewSet,
    BonoViewSet,
    ApprovalRequestViewSet
)

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employees')
router.register(r'evaluations', EvaluationViewSet, basename='evaluations')
router.register(r'bonos', BonoViewSet, basename='bonos')
router.register(r'approvals', ApprovalRequestViewSet, basename='approvals')

urlpatterns = [
    path('', include(router.urls)),
]