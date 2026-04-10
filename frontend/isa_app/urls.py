from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('evaluaciones/', views.evaluaciones, name='evaluaciones'),
    path('aprobaciones/', views.aprobaciones, name='aprobaciones'),
    path('reportes/', views.reportes, name='reportes'),
    path('bonos/', views.bonos, name='bonos'),
    path('usuarios/', views.usuarios, name='usuarios'),
]