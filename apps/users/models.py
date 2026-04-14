from django.db import models

class Usuarios(models.Model):
    id = models.UUIDField(primary_key=True)
    username = models.CharField(unique=True, max_length=50)
    rol = models.ForeignKey('CatRoles', models.DO_NOTHING)
    departamento = models.ForeignKey('CatDepartamentos', models.DO_NOTHING)
    manager = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)
    fecha_registro = models.DateTimeField(blank=True, null=True)
    password_hash = models.TextField()
    class Meta:
        managed = False
        db_table = 'usuarios'