"""mock_auth.py
Script de desarrollo para generar tokens JWT válidos simulando el Auth Service.
¡NO INCLUIR EN PRODUCCIÓN!
"""
import jwt
import uuid
from datetime import datetime, timedelta, timezone

# 1. Leer la llave privada de desarrollo que acabas de generar
try:
    with open("dev_private.pem", "r") as f:
        private_key = f.read()
except FileNotFoundError:
    print("Error: No se encontró 'dev_private.pem'. Ejecuta el comando de openssl primero.")
    exit(1)

# 2. Construir el Payload (El contenido del Gafete)
# Aquí puedes cambiar el 'sub' o el 'role' para probar cómo reacciona tu parche Anti-IDOR
payload = {
    "sub": "uuid-del-usuario-empleado-o-rrhh", # ID del usuario que hace la petición
    "role": "RRHH",                            # Rol del usuario
    "jti": str(uuid.uuid4()),                  # JWT ID (para probar la revocación en Redis)
    "iat": datetime.now(timezone.utc),
    "exp": datetime.now(timezone.utc) + timedelta(hours=2) # Expira en 2 horas
}

# 3. Firmar el token usando RS256 y la llave privada
token = jwt.encode(payload, private_key, algorithm="RS256")

print("=========================================================")
print(" TOKEN DE DESARROLLO GENERADO CON ÉXITO")
print("=========================================================\n")
print(token)
print("\n=========================================================")
print("Úsalo en Swagger o Postman como: Bearer <token>")