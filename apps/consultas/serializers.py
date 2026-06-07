from rest_framework import serializers
from apps.consultas.models import Consultas, Notificaciones


class ConsultaSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.nombre_completo', read_only=True)

    class Meta:
        model = Consultas
        fields = '__all__'


class ConsultaUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultas
        fields = ['respuesta', 'estado', 'fecha_respuesta']


class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificaciones
        fields = '__all__'
