from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from apps.users.models import Usuarios

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        """
        Sobrescribimos este método para buscar al usuario en nuestra 
        tabla de Supabase (UUID) en lugar de la tabla por defecto de Django (Entero).
        """
        try:
            user_id = validated_token.get('user_id')
            if not user_id:
                raise AuthenticationFailed('El token no contiene un ID de usuario válido', code='token_not_valid')

            # Buscamos en nuestro modelo personalizado usando el UUID
            user = Usuarios.objects.get(id=user_id)
            
            # Truco para que DRF no rechace al usuario por no tener el campo is_active
            if not hasattr(user, 'is_active'):
                user.is_active = True
                
            return user

        except Usuarios.DoesNotExist:
            raise AuthenticationFailed('Usuario no encontrado', code='user_not_found')
        except Exception as e:
            raise AuthenticationFailed(f'Error de autenticación: {str(e)}', code='authentication_error')