import uuid
from django.db import models


class Consultas(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey('users.Usuarios', models.DO_NOTHING, blank=True, null=True)
    nombre_usuario = models.CharField(max_length=255)
    pregunta = models.TextField()
    respuesta = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, default='pendiente')
    fecha = models.DateTimeField(auto_now_add=True)
    fecha_respuesta = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'consultas'


class Notificaciones(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    titulo = models.CharField(max_length=255)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=50, default='comunicado')
    para = models.CharField(max_length=50, default='todos')
    leido = models.BooleanField(default=False)
    fecha_limite = models.DateField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'notificaciones'
