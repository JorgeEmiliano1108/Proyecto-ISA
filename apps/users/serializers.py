from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.hashers import check_password
from .models import Usuarios


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer personalizado para login JWT con modelo Usuarios de Supabase.
    Valida contra password_hash usando PBKDF2.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

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

        if not check_password(password, usuario.password_hash):
            raise serializers.ValidationError({
                'detail': 'Credenciales inválidas',
                'code': 'invalid_credentials'
            })

        attrs['user'] = usuario
        return super().validate(attrs)

    @classmethod
    def get_token(cls, usuario):
        token = super().get_token(usuario)
        
        token['username'] = usuario.username
        token['nombre_completo'] = usuario.nombre_completo
        token['puesto'] = usuario.puesto
        token['rol_id'] = usuario.rol_id
        token['departamento_id'] = usuario.departamento_id
        
        return token


class UsuarioSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.CharField(read_only=True)
    
    class Meta:
        model = Usuarios
        fields = [
            'id', 'username', 'nombres', 'apellido_paterno', 
            'apellido_materno', 'puesto', 'nombre_completo',
            'rol', 'departamento', 'manager', 'fecha_registro'
        ]
        read_only_fields = ['id', 'fecha_registro']
