import uuid
from django.db import models
# 5 historial estados
class HistorialEstados(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    evaluacion = models.ForeignKey('evaluations.Evaluaciones', models.DO_NOTHING)
    estado_anterior = models.CharField(max_length=50)
    estado_nuevo = models.CharField(max_length=50)
    usuario = models.ForeignKey('users.Usuarios', models.DO_NOTHING)
    comentario = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'historial_estados'

# 6 aprobaciones
class Aprobaciones(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    evaluacion = models.ForeignKey('evaluations.Evaluaciones', models.DO_NOTHING)
    rol = models.ForeignKey('catalogs.CatRoles', models.DO_NOTHING)
    usuario = models.ForeignKey('users.Usuarios', models.DO_NOTHING)
    firma_digital_base64 = models.TextField()
    ip_address = models.CharField(max_length=45)
    fecha_firma = models.DateTimeField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'aprobaciones'
# 7 logs sistema
class LogsSistema(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey('users.Usuarios', models.DO_NOTHING, blank=True, null=True)
    accion = models.CharField(max_length=50)
    ip_address = models.CharField(max_length=45)
    detalle = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'logs_sistema'