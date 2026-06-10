#!/usr/bin/env python3
"""
Generador de tokens JWT para pruebas de bonus_service.

Este script genera tokens JWT válidos para probar los endpoints sin necesidad
de tener la base de datos configurada.

USO:
    # Generar token con usuario y roles por defecto
    python3 scripts/generate_test_token.py

    # Especificar usuario y roles
    python3 scripts/generate_test_token.py --user admin --roles admin,finanzas

    # Token que expira en 48 horas
    python3 scripts/generate_test_token.py --user test-user --expires 48

    # Ver ayuda
    python3 scripts/generate_test_token.py --help

EJEMPLO DE USO CON CURL:
    # 1. Generar token
    TOKEN=$(python3 scripts/generate_test_token.py --quiet)

    # 2. Usar en endpoint de bonus
    curl -X POST http://localhost:8002/api/v1/bonus/calculate \\
      -H "Authorization: Bearer $TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{"evaluacion_id": "550e8400-e29b-41d4-a716-446655440000", "calificacion_global": 4.0}'

NOTA:
    Este script solo funciona cuando DEBUG_MODE=true está configurado.
"""
import argparse
import jwt
from datetime import datetime, timedelta
import os
import sys

# Agregar el directorio padre al path para importar config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.core.config import settings
except ImportError:
    print("❌ Error: No se pudo importar la configuración.")
    print("   Asegúrate de estar ejecutando este script desde el directorio raíz del proyecto.")
    sys.exit(1)


def generate_token(user_id: str, roles: list, expires_hours: int = 24) -> str:
    """
    Genera un token JWT válido para pruebas.
    
    Args:
        user_id: Identificador del usuario
        roles: Lista de roles del usuario
        expires_hours: Horas hasta que expire el token
    
    Returns:
        Token JWT codificado
    """
    # Obtener la clave secreta (prioridad: JWT_SECRET_KEY > SECRET_KEY > fallback)
    secret = (
        os.environ.get("JWT_SECRET_KEY") or
        os.environ.get("SECRET_KEY") or
        "dev-secret-change-in-production-do-not-use"
    )
    
    payload = {
        "sub": user_id,
        "roles": roles,
        "exp": datetime.utcnow() + timedelta(hours=expires_hours),
        "iat": datetime.utcnow(),
        "jti": f"mock-{datetime.utcnow().isoformat()}"
    }
    
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token


def main():
    parser = argparse.ArgumentParser(
        description="Generar token JWT para pruebas de bonus_service",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Token por defecto (user=test-user, roles=admin,finanzas, 24h)
  python3 scripts/generate_test_token.py

  # Usuario y roles específicos
  python3 scripts/generate_test_token.py --user admin --roles admin,finanzas

  # Token que expira en 48 horas
  python3 scripts/generate_test_token.py --expires 48

  # Modo silencioso (solo el token)
  python3 scripts/generate_test_token.py --quiet
        """
    )
    
    parser.add_argument(
        "--user", "-u",
        default="test-user",
        help="ID del usuario (default: test-user)"
    )
    
    parser.add_argument(
        "--roles", "-r",
        default="admin,finanzas",
        help="Roles separados por coma (default: admin,finanzas)"
    )
    
    parser.add_argument(
        "--expires", "-e",
        type=int,
        default=24,
        help="Horas de expiración (default: 24)"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Solo imprimir el token (útil para scripts)"
    )
    
    args = parser.parse_args()
    
    # Verificar DEBUG_MODE
    if not settings.DEBUG_MODE:
        if not args.quiet:
            print("⚠️  WARNING: DEBUG_MODE no está activado en .env")
            print("   El token podría no funcionar si el servicio tiene DEBUG_MODE=false")
            print("   Para activarlo, agrega DEBUG_MODE=true a tu archivo .env")
            print()
    
    # Parsear roles
    roles = [r.strip() for r in args.roles.split(",")]
    
    # Generar token
    token = generate_token(args.user, roles, args.expires)
    
    if args.quiet:
        # Modo silencioso: solo el token
        print(token)
    else:
        # Modo normal: información detallada
        print(f"✅ Token generado para usuario: {args.user}")
        print(f"📋 Roles: {', '.join(roles)}")
        print(f"⏰ Expira en: {args.expires} horas")
        print(f"🕐 Generado: {datetime.utcnow().isoformat()} UTC")
        print()
        print(f"🔑 Token JWT:")
        print(f"{token}")
        print()
        print(f"💡 Uso en curl:")
        print(f'curl -X POST http://localhost:8002/api/v1/bonus/calculate \\')
        print(f'  -H "Authorization: Bearer {token}" \\')
        print(f'  -H "Content-Type: application/json" \\')
        print(f'  -d \'{{"evaluacion_id": "550e8400-e29b-41d4-a716-446655440000", "calificacion_global": 4.0}}\'')
        print()
        print(f"💡 O usa este endpoint mockeado (más simple):")
        print(f'curl -X POST http://localhost:8002/api/v1/auth/mock-login \\')
        print(f'  -H "Content-Type: application/json" \\')
        print(f'  -d \'{{"username": "{args.user}"}}\'')


if __name__ == "__main__":
    main()