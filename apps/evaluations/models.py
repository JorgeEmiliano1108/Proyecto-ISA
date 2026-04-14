from django.db import models

class Evaluaciones(models.Model):
    id = models.UUIDField(primary_key=True)
    evaluado = models.ForeignKey('Usuarios', models.DO_NOTHING)
    evaluador = models.ForeignKey('Usuarios', models.DO_NOTHING, related_name='evaluaciones_evaluador_set')
    periodo = models.ForeignKey('CatPeriodos', models.DO_NOTHING)
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

class CompetenciasDetalle(models.Model):
    id = models.UUIDField(primary_key=True)
    evaluacion = models.ForeignKey('Evaluaciones', models.DO_NOTHING)
    competencia = models.ForeignKey('CatCompetencias', models.DO_NOTHING)
    calificacion = models.IntegerField(blank=True, null=True)
    comentario = models.TextField()
    class Meta:
        managed = False
        db_table = 'competencias_detalle'

class Objetivos(models.Model):
    id = models.UUIDField(primary_key=True)
    evaluacion = models.ForeignKey('Evaluaciones', models.DO_NOTHING)
    descripcion = models.TextField()
    class Meta:
        managed = False
        db_table = 'objetivos'