"""
URLs for Finances app - Bonos integration.
"""
from django.urls import path
from .views import (
    CalculateBonoView,
    CalculateBonoBatchView,
    BonoReportView,
    BonoListView,
)

urlpatterns = [
    path('bonos/calculate/', CalculateBonoView.as_view(), name='bono-calculate'),
    path('bonos/calculate/batch/', CalculateBonoBatchView.as_view(), name='bono-batch-calculate'),
    path('bonos/report/<int:periodo_id>/', BonoReportView.as_view(), name='bono-report'),
    path('bonos/calculos/', BonoListView.as_view(), name='bono-list'),
]