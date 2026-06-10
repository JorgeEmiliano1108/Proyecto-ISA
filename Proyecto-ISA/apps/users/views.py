from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import Usuarios
from .serializers import (
    CustomTokenObtainPairSerializer,
    UsuarioSerializer,
    UsuarioCreateSerializer
)


# ============================================
# VISTAS DE AUTENTICACIÓN
# ============================================

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Vista customizada para login JWT.
    Endpoint: POST /api/v1/auth/login/
    """
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]


class TokenRefreshView(TokenRefreshView):
    """
    Vista para refresh de token.
    Endpoint: POST /api/v1/auth/refresh/
    """
    pass


# ============================================
# PERMISOS RBAC
# ============================================

class IsAdminOrContraloria(BasePermission):
    """
    Permite acceso total solo a Administradores y Contraloría.
    Los demás usuarios solo pueden consultar (GET).
    """
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        user_rol = getattr(getattr(request, 'user', None), 'rol', None)
        if user_rol:
            return user_rol.nombre.lower() in ['administrador', 'contraloria']
        return False


# ============================================
# VIEW SET DE USUARIOS
# ============================================

class UsuarioViewSet(viewsets.ModelViewSet):
    """
    CRUD de usuarios con permisos RBAC.
    """
    queryset = Usuarios.objects.all().order_by('-fecha_registro')
    permission_classes = [IsAuthenticated, IsAdminOrContraloria]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return UsuarioCreateSerializer
        return UsuarioSerializer