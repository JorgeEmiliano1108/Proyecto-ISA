from rest_framework import serializers
from .models import CatRoles, CatDepartamentos, CatPeriodos, CatCompetencias


class CatRolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatRoles
        fields = ['id', 'nombre', 'nivel_aprobacion', 'activo']


class CatDepartamentosSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatDepartamentos
        fields = ['id', 'nombre', 'activo']


class CatPeriodosSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatPeriodos
        fields = ['id', 'nombre', 'activo']


class CatCompetenciasSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatCompetencias
        fields = ['id', 'nombre', 'descripcion', 'activo']
