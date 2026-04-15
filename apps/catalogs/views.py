from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import CatRoles, CatDepartamentos, CatPeriodos, CatCompetencias
from .serializers import (
    CatRolesSerializer,
    CatDepartamentosSerializer,
    CatPeriodosSerializer,
    CatCompetenciasSerializer
)


class CatRolesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only para roles.
    """
    queryset = CatRoles.objects.filter(activo=True)
    serializer_class = CatRolesSerializer
    permission_classes = [IsAuthenticated]


class CatDepartamentosViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only para departamentos.
    """
    queryset = CatDepartamentos.objects.filter(activo=True)
    serializer_class = CatDepartamentosSerializer
    permission_classes = [IsAuthenticated]


class CatPeriodosViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only para periodos.
    """
    queryset = CatPeriodos.objects.filter(activo=True)
    serializer_class = CatPeriodosSerializer
    permission_classes = [IsAuthenticated]


class CatCompetenciasViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only para competencias.
    """
    queryset = CatCompetencias.objects.filter(activo=True)
    serializer_class = CatCompetenciasSerializer
    permission_classes = [IsAuthenticated]
