from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import CustomTokenObtainPairSerializer, UsuarioSerializer
from .models import Usuarios


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


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    CRUD de usuarios.
    Endpoints: /api/v1/users/
    """
    queryset = Usuarios.objects.select_related('rol', 'departamento', 'manager')
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        usuario = self.request.user
        return self.queryset.filter(departamento=usuario.departamento)
