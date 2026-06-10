from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.consultas.views import ConsultaViewSet, NotificacionViewSet

app_name = 'consultas'

router = DefaultRouter()
router.register(r'consultas', ConsultaViewSet, basename='consultas')
router.register(r'notificaciones', NotificacionViewSet, basename='notificaciones')

urlpatterns = [
    path('', include(router.urls)),
]
