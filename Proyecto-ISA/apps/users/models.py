import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UsuariosManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('El username es obligatorio')
        user = self.model(username=username, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        return self.create_user(username, password, **extra_fields)


class Usuarios(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(unique=True, max_length=50)
    nombre_completo = models.CharField(max_length=255, blank=True, null=True)
    puesto = models.CharField(max_length=100, blank=True, null=True)
    id_persona_empleado = models.IntegerField(unique=True, blank=True, null=True)
    id_area_siare = models.IntegerField(blank=True, null=True)
    id_puesto_siare = models.IntegerField(blank=True, null=True)
    rol = models.ForeignKey('catalogs.CatRoles', models.DO_NOTHING)
    departamento = models.ForeignKey('catalogs.CatDepartamentos', models.DO_NOTHING)
    manager = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)
    fecha_registro = models.DateTimeField(blank=True, null=True)

    objects = UsuariosManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        managed = False
        db_table = 'usuarios'

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_active(self):
        return True

    @property
    def is_staff(self):
        return False

    @property
    def is_superuser(self):
        return False
