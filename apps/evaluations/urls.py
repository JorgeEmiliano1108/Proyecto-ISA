"""
URLs para Evaluaciones.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.evaluations.views import EvaluacionViewSet

app_name = 'evaluations'

router = DefaultRouter()
router.register(r'', EvaluacionViewSet, basename='evaluaciones')

urlpatterns = [
    path('', include(router.urls)),
]
