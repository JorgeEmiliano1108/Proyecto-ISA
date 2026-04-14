from django.db import models

class HistorialEstados(models.Model):
    id = models.UUIDField(primary_key=True)
    evaluacion = models.ForeignKey('Evaluaciones', models.DO_NOTHING)
    estado_anterior = models.CharField(max_length=50)
    estado_nuevo = models.CharField(max_length=50)
    usuario = models.ForeignKey('Usuarios', models.DO_NOTHING)
    comentario = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'historial_estados'

class Aprobaciones(models.Model):
    id = models.UUIDField(primary_key=True)
    evaluacion = models.ForeignKey('Evaluaciones', models.DO_NOTHING)
    rol = models.ForeignKey('CatRoles', models.DO_NOTHING)
    usuario = models.ForeignKey('Usuarios', models.DO_NOTHING)
    firma_digital_base64 = models.TextField()
    ip_address = models.CharField(max_length=45)
    fecha_firma = models.DateTimeField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'aprobaciones'

class LogsSistema(models.Model):
    id = models.UUIDField(primary_key=True)
    usuario = models.ForeignKey('Usuarios', models.DO_NOTHING, blank=True, null=True)
    accion = models.CharField(max_length=50)
    ip_address = models.CharField(max_length=45)
    detalle = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'logs_sistema'