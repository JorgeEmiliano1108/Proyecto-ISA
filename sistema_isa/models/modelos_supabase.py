"""
[SISTEMA ISA] - Conexión a Supabase (PostgreSQL) ¡ESTABLECIDA CON ÉXITO!

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


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


class Bonos(models.Model):
    id = models.UUIDField(primary_key=True)
    evaluacion = models.ForeignKey('Evaluaciones', models.DO_NOTHING)
    salario_base_snapshot = models.DecimalField(max_digits=12, decimal_places=2)
    impacto_ebitda_logrado = models.DecimalField(max_digits=5, decimal_places=2)
    performance_index = models.DecimalField(max_digits=5, decimal_places=2)
    monto_final_bono = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_calculo = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bonos'


class CatCompetencias(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cat_competencias'


class CatDepartamentos(models.Model):
    nombre = models.CharField(unique=True, max_length=100)
    activo = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cat_departamentos'


class CatPeriodos(models.Model):
    nombre = models.CharField(unique=True, max_length=50)
    activo = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cat_periodos'


class CatRoles(models.Model):
    nombre = models.CharField(unique=True, max_length=50)
    nivel_aprobacion = models.IntegerField()
    activo = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cat_roles'


class CompetenciasDetalle(models.Model):
    id = models.UUIDField(primary_key=True)
    evaluacion = models.ForeignKey('Evaluaciones', models.DO_NOTHING)
    competencia = models.ForeignKey(CatCompetencias, models.DO_NOTHING)
    calificacion = models.IntegerField(blank=True, null=True)
    comentario = models.TextField()

    class Meta:
        managed = False
        db_table = 'competencias_detalle'


class Evaluaciones(models.Model):
    id = models.UUIDField(primary_key=True)
    evaluado = models.ForeignKey('Usuarios', models.DO_NOTHING)
    evaluador = models.ForeignKey('Usuarios', models.DO_NOTHING, related_name='evaluaciones_evaluador_set')
    periodo = models.ForeignKey(CatPeriodos, models.DO_NOTHING)
    estado = models.CharField(max_length=50, blank=True, null=True)
    logros_previos = models.TextField(blank=True, null=True)
    comentarios_evaluador = models.TextField(blank=True, null=True)
    comentarios_evaluado = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)
    fecha_actualizacion = models.DateTimeField(blank=True, null=True)
    fecha_ultimo_recordatorio = models.DateTimeField(blank=True, null=True)
    calificacion_global = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'evaluaciones'


class HistorialEstados(models.Model):
    id = models.UUIDField(primary_key=True)
    evaluacion = models.ForeignKey(Evaluaciones, models.DO_NOTHING)
    estado_anterior = models.CharField(max_length=50)
    estado_nuevo = models.CharField(max_length=50)
    usuario = models.ForeignKey('Usuarios', models.DO_NOTHING)
    comentario = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'historial_estados'


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


class Objetivos(models.Model):
    id = models.UUIDField(primary_key=True)
    evaluacion = models.ForeignKey(Evaluaciones, models.DO_NOTHING)
    descripcion = models.TextField()

    class Meta:
        managed = False
        db_table = 'objetivos'


class Usuarios(models.Model):
    id = models.UUIDField(primary_key=True)
    username = models.CharField(unique=True, max_length=50)
    rol = models.ForeignKey(CatRoles, models.DO_NOTHING)
    departamento = models.ForeignKey(CatDepartamentos, models.DO_NOTHING)
    manager = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)
    fecha_registro = models.DateTimeField(blank=True, null=True)
    password_hash = models.TextField()

    class Meta:
        managed = False
        db_table = 'usuarios'
"""