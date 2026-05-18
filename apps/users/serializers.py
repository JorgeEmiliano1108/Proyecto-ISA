from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.hashers import check_password, make_password
from .models import Usuarios


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
        token['departamento_id'] = usuario.departamento_id
        return token

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

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
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        return data


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
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

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
