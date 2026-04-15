from django.db import models

class Usuarios(models.Model):
    id = models.UUIDField(primary_key=True)
    username = models.CharField(unique=True, max_length=50)    
    nombres = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100, blank=True, null=True)
    puesto = models.CharField(max_length=100, blank=True, null=True)
    rol = models.ForeignKey('catalogs.CatRoles', models.DO_NOTHING)
    departamento = models.ForeignKey('catalogs.CatDepartamentos', models.DO_NOTHING)
    manager = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)
    fecha_registro = models.DateTimeField(blank=True, null=True)
    password_hash = models.TextField()

    class Meta:
        managed = False
        db_table = 'usuarios'

    # Método property sugerido por el DBA para el PDF y el Frontend
    @property
    def nombre_completo(self):
        if self.apellido_materno:
            return f"{self.nombres} {self.apellido_paterno} {self.apellido_materno}"
        return f"{self.nombres} {self.apellido_paterno}"