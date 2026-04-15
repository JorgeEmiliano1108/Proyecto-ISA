from django.db import models
# 8 evaluaciones
class Evaluaciones(models.Model):
    id = models.UUIDField(primary_key=True)
    evaluado = models.ForeignKey('users.Usuarios', models.DO_NOTHING)
    evaluador = models.ForeignKey('users.Usuarios', models.DO_NOTHING, related_name='evaluaciones_evaluador_set')
    periodo = models.ForeignKey('catalogs.CatPeriodos', models.DO_NOTHING)
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
# 9 competencias detalle
class CompetenciasDetalle(models.Model):
    id = models.UUIDField(primary_key=True)
    evaluacion = models.ForeignKey('evaluations.Evaluaciones', models.DO_NOTHING)
    competencia = models.ForeignKey('catalogs.CatCompetencias', models.DO_NOTHING)
    calificacion = models.IntegerField(blank=True, null=True)
    comentario = models.TextField()
    class Meta:
        managed = False
        db_table = 'competencias_detalle'
# 10 objetivos
class Objetivos(models.Model):
    id = models.UUIDField(primary_key=True)
    evaluacion = models.ForeignKey('evaluations.Evaluaciones', models.DO_NOTHING)
    descripcion = models.TextField()
    class Meta:
        managed = False
        db_table = 'objetivos'