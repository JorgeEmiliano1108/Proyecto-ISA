from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from apps.consultas.models import Consultas, Notificaciones
from apps.consultas.serializers import (
    ConsultaSerializer,
    ConsultaUpdateSerializer,
    NotificacionSerializer
)


class ConsultaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Consultas.objects.all().order_by('-fecha')

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return ConsultaUpdateSerializer
        return ConsultaSerializer

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user, nombre_usuario=self.request.user.nombre_completo)

    def get_queryset(self):
        qs = super().get_queryset()
        estado = self.request.query_params.get('estado')
        if estado:
            qs = qs.filter(estado=estado)
        return qs


class NotificacionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Notificaciones.objects.all().order_by('-fecha_creacion')
    serializer_class = NotificacionSerializer
