# app/core/security.py
import re
import json
import hmac
import hashlib
import bleach
from typing import Any, Dict


# Input Validation & XSS Prevention


# Configuramos bleach para ser extremadamente restrictivo.
# Como es un sistema interno de RRHH, no deberíamos aceptar HTML en los logs.
ALLOWED_TAGS = []
ALLOWED_ATTRIBUTES = {}

def sanitize_text(text: str | None) -> str:
    """
    Sanitiza cadenas de texto eliminando cualquier etiqueta HTML o script malicioso.
    Aplica el principio OWASP de Output Encoding / Input Validation.
    """
    if not text:
        return ""
    
    # bleach.clean elimina etiquetas no permitidas y escapa caracteres peligrosos
    sanitized = bleach.clean(
        text,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True # Elimina el contenido malicioso en lugar de solo escaparlo
    )
    return sanitized.strip()

def sanitize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recorre recursivamente un diccionario (ej. details del log) y sanitiza 
    todos los valores de tipo string.
    """
    sanitized_dict = {}
    for key, value in payload.items():
        if isinstance(value, str):
            sanitized_dict[key] = sanitize_text(value)
        elif isinstance(value, dict):
            sanitized_dict[key] = sanitize_payload(value)
        elif isinstance(value, list):
            sanitized_dict[key] = [
                sanitize_text(item) if isinstance(item, str) else item 
                for item in value
            ]
        else:
            sanitized_dict[key] = value
    return sanitized_dict



# Minimización y Enmascaramiento (Data Masking)


# Regex para detectar correos electrónicos corporativos o personales
EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')

def mask_pii(text: str) -> str:
    """
    Detecta y enmascara Información Personal Identificable (PII) en textos libres.
    Ejemplo: "Aprobado por juan.perez@empresa.com" -> "Aprobado por j********z@empresa.com"
    Cumplimiento LFPDPPP: Minimización de datos en logs.
    """
    if not text:
        return ""

    def mask_email(match):
        email = match.group(0)
        local_part, domain = email.split('@')
        if len(local_part) > 2:
            masked_local = f"{local_part[0]}{'*' * (len(local_part)-2)}{local_part[-1]}"
        else:
            masked_local = "*" * len(local_part)
        return f"{masked_local}@{domain}"

    return EMAIL_REGEX.sub(mask_email, text)


# Cryptographic Practices & Tamper-Evidence

def generate_log_signature(log_data: Dict[str, Any], secret_key: str) -> str:
    """
    Genera un HMAC-SHA256 del contenido del log.
    Propósito: Garantizar la inmutabilidad. Si un administrador de BD altera
    un registro (ej. cambia 'REJECTED' a 'APPROVED'), la firma ya no coincidirá.
    """
    # Ordenamos las llaves para garantizar que el JSON stringificado sea determinista
    canonical_json = json.dumps(log_data, sort_keys=True, separators=(',', ':'))
    
    signature = hmac.new(
        key=secret_key.encode('utf-8'),
        msg=canonical_json.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()
    
    return signature

def verify_log_signature(log_data: Dict[str, Any], signature: str, secret_key: str) -> bool:
    """
    Verifica si un log ha sido alterado desde su creación comparando firmas HMAC en tiempo constante
    para evitar ataques de timing (OWASP).
    """
    expected_signature = generate_log_signature(log_data, secret_key)
    return hmac.compare_digest(expected_signature, signature)