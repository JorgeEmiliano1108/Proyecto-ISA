from django.db import models

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