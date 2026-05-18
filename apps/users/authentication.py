from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from apps.users.models import Usuarios


class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            user_id = validated_token.get('user_id')
            if not user_id:
                raise AuthenticationFailed('El token no contiene un ID de usuario válido', code='token_not_valid')

            user = Usuarios.objects.get(id=user_id)
            return user

        except Usuarios.DoesNotExist:
            raise AuthenticationFailed('Usuario no encontrado', code='user_not_found')
        except Exception as e:
            raise AuthenticationFailed(f'Error de autenticación: {str(e)}', code='authentication_error')
