"""
Filtro de Logging para OWASP A09 - Security Logging and Monitoring.

Censura palabras sensibles antes de imprimir logs en consola/Docker.
"""
import logging
import re
from typing import Any, Optional


SENSITIVE_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r'(?<![a-zA-Z0-9])("password"\s*:\s*")[^"]*(")'), r'\1***REDACTED***\3'),
    (re.compile(r'(?<![a-zA-Z0-9])("token"\s*:\s*")[^"]*(")'), r'\1***REDACTED***\3'),
    (re.compile(r'(?<![a-zA-Z0-9])("authorization"\s*:\s*")[^"]*(")'), r'\1***REDACTED***\3'),
    (re.compile(r'(?<![a-zA-Z0-9])("bearer"\s*:\s*")[^"]*(")'), r'\1***REDACTED***\3'),
    (re.compile(r'(?<![a-zA-Z0-9])("secret"\s*:\s*")[^"]*(")'), r'\1***REDACTED***\3'),
    (re.compile(r'(?<![a-zA-Z0-9])("encryption_key"\s*:\s*")[^"]*(")'), r'\1***REDACTED***\3'),
    (re.compile(r'(?<![a-zA-Z0-9])("secret_key"\s*:\s*")[^"]*(")'), r'\1***REDACTED***\3'),
    (re.compile(r'(?<![a-zA-Z0-9])("db_password"\s*:\s*")[^"]*(")'), r'\1***REDACTED***\3'),
    (re.compile(r'Bearer\s+[A-Za-z0-9_.-]+'), r'Bearer ***REDACTED***'),
    (re.compile(r'password=[^&\s]*'), r'password=***REDACTED***'),
    (re.compile(r'token=[^&\s]*'), r'token=***REDACTED***'),
]

SENSITIVE_HEADERS = {
    "authorization",
    "x-api-key",
    "x-auth-token",
    "cookie",
    "set-cookie",
}


class SensitiveDataFilter(logging.Filter):
    """
    Filtro que censuran datos sensibles en mensajes de log.
    
    OWASP A09: Security Logging and Monitoring Failures
    - Enmascara tokens, passwords y datos sensibles en logs
    - Previene filtraciones en consola Docker
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if record.msg and isinstance(record.msg, str):
            record.msg = self._censor(record.msg)

        if record.args:
            record.args = tuple(
                self._censor(str(arg)) if isinstance(arg, str) else arg
                for arg in record.args
            )

        if hasattr(record, "request_id"):
            record.request_id = record.request_id

        return True

    @classmethod
    def _censor(cls, text: str) -> str:
        """Aplica censura a patrones sensibles."""
        for pattern, _ in SENSITIVE_PATTERNS:
            text = pattern.sub(lambda m: m.group(0)[:m.start(1) if m.start(1) > -1 else m.group(0)], text)

        text = re.sub(
            r'(?<![a-zA-Z0-9])("password"|"token"|"authorization"|"secret")[^\n"]{0,50}',
            r'\1: ***REDACTED***',
            text,
            flags=re.IGNORECASE,
        )

        return text


def anonymize_ip(ip: Optional[str]) -> Optional[str]:
    """
    Anonimiza parcialmente la IP del cliente.
    Solo mantiene los primeros dos octetos para IPv4.
    """
    if not ip:
        return None

    if "." in ip and ":" not in ip:
        parts = ip.split(".")
        if len(parts) >= 2:
            return f"{parts[0]}.{parts[1]}.***.***"

    if ":" in ip:
        return f"{ip[:4]}:***:***:***"

    return "***.***.***.***"


def setup_secure_logging() -> None:
    """Configura el logging global con filtro de datos sensibles."""
    sensitive_filter = SensitiveDataFilter()

    for handler in logging.root.handlers:
        handler.addFilter(sensitive_filter)

    logging.getLogger("uvicorn.access").addFilter(sensitive_filter)
    logging.getLogger("uvicorn.error").addFilter(sensitive_filter)
    logging.getLogger("uvicorn").addFilter(sensitive_filter)