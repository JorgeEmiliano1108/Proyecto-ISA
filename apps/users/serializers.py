import uuid
import logging
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone
from .models import Usuarios
from apps.catalogs.models import CatRoles, CatDepartamentos
from .ad_client import ISAClient

logger = logging.getLogger(__name__)

ROLE_KEYWORDS = [
    ('director', 'Director'),
    ('gerente', 'Gerente'),
    ('coordinador', 'Coordinador'),
    ('contralor', 'Contraloria'),
]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    @classmethod
    def get_token(cls, usuario):
        token = super().get_token(usuario)
        token['username'] = usuario.username
        token['nombre_completo'] = usuario.nombre_completo
        token['puesto'] = usuario.puesto
        token['rol_id'] = usuario.rol_id
        token['rol_nombre'] = usuario.rol.nombre if usuario.rol else None
        token['departamento_id'] = usuario.departamento_id
        return token

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        ad_result = ISAClient().validar_acceso(username, password)

        if ad_result is None:
            return self._validar_local(username, password)

        if ad_result.get('accesoValido'):
            usuario = self._jit_provisioning(username)
            if usuario:
                refresh = self.get_token(usuario)
                return {'refresh': str(refresh), 'access': str(refresh.access_token)}

        raise serializers.ValidationError({
            'detail': 'Credenciales inválidas',
            'code': 'invalid_credentials'
        })

    def _validar_local(self, username, password):
        try:
            usuario = Usuarios.objects.select_related('rol', 'departamento').get(
                username=username
            )
        except Usuarios.DoesNotExist:
            raise serializers.ValidationError({
                'detail': 'Credenciales inválidas',
                'code': 'invalid_credentials'
            })

        if not check_password(password, usuario.password):
            raise serializers.ValidationError({
                'detail': 'Credenciales inválidas',
                'code': 'invalid_credentials'
            })

        refresh = self.get_token(usuario)
        return {'refresh': str(refresh), 'access': str(refresh.access_token)}

    def _jit_provisioning(self, username):
        persona = ISAClient().consultar_persona(username)
        if not persona:
            return None

        rol = self._mapear_rol(persona.get('puesto', ''))
        depto = self._mapear_departamento(persona.get('area', ''))

        manager = None
        evaluador_username = persona.get('userNameEvaluador')
        if evaluador_username:
            try:
                manager = Usuarios.objects.get(username=evaluador_username)
            except Usuarios.DoesNotExist:
                pass

        id_persona_empleado = persona.get('idPersonaEmpleado')
        if id_persona_empleado is not None:
            Usuarios.objects.filter(
                id_persona_empleado=id_persona_empleado
            ).exclude(username=username).update(id_persona_empleado=None)

        usuario, created = Usuarios.objects.update_or_create(
            username=username,
            defaults={
                'nombre_completo': persona.get('nombreCompleto', ''),
                'puesto': persona.get('puesto', ''),
                'id_persona_empleado': id_persona_empleado,
                'id_area_siare': persona.get('idArea'),
                'id_puesto_siare': persona.get('idPuesto'),
                'rol': rol,
                'departamento': depto,
                'manager': manager,
                'fecha_registro': timezone.now(),
            }
        )
        if created:
            usuario.password = make_password(uuid.uuid4().hex)
            usuario.save(update_fields=['password'])

        logger.info(
            f'JIT: Usuario {"creado" if created else "actualizado"}: {username}'
        )
        return usuario

    @staticmethod
    def _mapear_rol(puesto_nombre):
        role_name = 'Colaborador'
        for keyword, nombre_rol in ROLE_KEYWORDS:
            if puesto_nombre.lower().startswith(keyword):
                role_name = nombre_rol
                break
        try:
            return CatRoles.objects.get(nombre__iexact=role_name)
        except CatRoles.DoesNotExist:
            return CatRoles.objects.create(
                nombre=role_name, nivel_aprobacion=0, activo=True
            )

    @staticmethod
    def _mapear_departamento(area_nombre):
        nombre = (area_nombre or '').strip() or 'Sin área'
        try:
            return CatDepartamentos.objects.get(nombre__iexact=nombre)
        except CatDepartamentos.DoesNotExist:
            return CatDepartamentos.objects.create(
                nombre=nombre, activo=True
            )


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuarios
        fields = [
            'id', 'username', 'nombre_completo', 'puesto',
            'id_persona_empleado', 'id_area_siare', 'id_puesto_siare',
            'rol', 'departamento', 'manager', 'fecha_registro'
        ]
        read_only_fields = ['id', 'fecha_registro']


class UsuarioCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, style={'input_type': 'password'}
    )

    class Meta:
        model = Usuarios
        fields = [
            'username', 'password', 'nombre_completo', 'puesto',
            'id_persona_empleado', 'id_area_siare', 'id_puesto_siare',
            'rol', 'departamento', 'manager'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['password'] = make_password(password)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            validated_data['password'] = make_password(password)
        return super().update(instance, validated_data)
