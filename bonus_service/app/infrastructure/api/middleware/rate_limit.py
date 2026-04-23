"""
Middleware de Rate Limiting y protección contra ataques de fuerza bruta.
Cumple: OWASP Secure-by-Design + OWASP SCP (Rate Limiting).

LIMITES:
- 100 requests/minuto por IP (límite general)
- 10 intentos de autenticación fallidos por IP (ventana de 15 minutos)
- Bloqueo temporal de 15 minutos después de 10 intentos fallidos
"""
from fastapi import Request, HTTPException, Response
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address as _get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time
from collections import defaultdict
from threading import Lock


logger = logging.getLogger(__name__)

limiter = Limiter(
    key_func=_get_remote_address,
    default_limits=["100/minute"],
    storage_uri="memory://",
)


class FailedAuthTracker:
    """
    Tracker de intentos de autenticación fallidos.
    
    OWASP Secure-by-Design: Implementa defensa contra ataques de fuerza bruta
    al token de autenticación.
    
    - Limita a 10 intentos fallidos por IP en ventana de 15 minutos
    - Después de 10 fallos, bloquea la IP por 15 minutos
    """
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init()
        return cls._instance
    
    def _init(self):
        self._attempts: dict[str, list[float]] = defaultdict(list)
        self._blocked_ips: dict[str, float] = {}
        self._cleanup_interval = 300
        self._last_cleanup = time.time()
    
    def _cleanup_old_entries(self):
        """Limpia entradas expiradas cada 5 minutos."""
        current_time = time.time()
        if current_time - self._last_cleanup < self._cleanup_interval:
            return
        
        self._last_cleanup = current_time
        cutoff_time = current_time - (15 * 60)
        
        for ip in list(self._attempts.keys()):
            self._attempts[ip] = [t for t in self._attempts[ip] if t > cutoff_time]
            if not self._attempts[ip]:
                del self._attempts[ip]
        
        for ip in list(self._blocked_ips.keys()):
            if self._blocked_ips[ip] < current_time:
                del self._blocked_ips[ip]
    
    def record_failed_attempt(self, ip: str) -> tuple[bool, int]:
        """
        Registra un intento de autenticación fallido.
        
        Returns:
            tuple: (is_blocked, remaining_attempts)
        """
        self._cleanup_old_entries()
        current_time = time.time()
        
        if ip in self._blocked_ips:
            if self._blocked_ips[ip] > current_time:
                return True, 0
            else:
                del self._blocked_ips[ip]
        
        window_start = current_time - (15 * 60)
        self._attempts[ip] = [t for t in self._attempts[ip] if t > window_start]
        self._attempts[ip].append(current_time)
        
        attempt_count = len(self._attempts[ip])
        remaining = max(0, 10 - attempt_count)
        
        if attempt_count >= 10:
            self._blocked_ips[ip] = current_time + (15 * 60)
            logger.warning(f"IP {ip} bloqueada por 15 minutos tras {attempt_count} intentos fallidos")
            self._attempts[ip] = []
            return True, 0
        
        return False, remaining
    
    def record_success(self, ip: str):
        """Limpia intentos fallidos tras éxito."""
        if ip in self._attempts:
            del self._attempts[ip]
        if ip in self._blocked_ips:
            del self._blocked_ips[ip]
    
    def is_blocked(self, ip: str) -> tuple[bool, int]:
        """Verifica si una IP está bloqueada y retorna segundos restantes."""
        self._cleanup_old_entries()
        current_time = time.time()
        
        if ip in self._blocked_ips:
            blocked_until = self._blocked_ips[ip]
            if blocked_until > current_time:
                remaining = int(blocked_until - current_time)
                return True, remaining
            else:
                del self._blocked_ips[ip]
        
        return False, 0
    
    def get_stats(self) -> dict:
        """Retorna estadísticas del tracker (para métricas)."""
        self._cleanup_old_entries()
        return {
            "tracked_ips": len(self._attempts),
            "blocked_ips": len(self._blocked_ips),
        }


failed_auth_tracker = FailedAuthTracker()


def get_remote_address(request: Request) -> str:
    """Obtiene IP del cliente considerando proxies (X-Forwarded-For)."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def rate_limit_middleware(request: Request, call_next):
    """
    Middleware de rate limiting con protección contra fuerza bruta.
    
    OWASP SCP:
    - Rate Limiting: Limitar número de requests por IP
    - Brute Force Protection: Registrar y bloquear IPs con muchos fallos
    
    Args:
        request: Request de FastAPI
        call_next: Función para continuar el request
        
    Returns:
        Response con headers de rate limiting o error 429
    """
    client_ip = get_remote_address(request)
    path = request.url.path
    
    if path.startswith("/api/"):
        is_blocked, remaining_time = failed_auth_tracker.is_blocked(client_ip)
        
        if is_blocked:
            logger.warning(f"Request bloqueado para IP: {client_ip} - tiempo restante: {remaining_time}s")
            return JSONResponse(
                status_code=429,
                content={
                    "detail": f"Demasiadas solicitudes. Bloqueado temporalmente. Intenta en {remaining_time} segundos.",
                },
                headers={
                    "Retry-After": str(remaining_time),
                    "X-RateLimit-Limit": "100/minute",
                    "X-RateLimit-Remaining": "0",
                }
            )
    
    try:
        response = await call_next(request)
        
        if hasattr(response, 'headers'):
            response.headers["X-RateLimit-Limit"] = "100/minute"
        
        return response
        
    except RateLimitExceeded as exc:
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        return JSONResponse(
            status_code=429,
            content={"detail": "Demasiadas solicitudes. Por favor, inténtalo más tarde."},
            headers={"Retry-After": "60"},
        )
    except Exception as exc:
        logger.error(f"Error en rate limit middleware: {exc}", exc_info=False)
        raise


class RateLimitProtectionMiddleware(BaseHTTPMiddleware):
    """
    Middleware adicional para protección específica de endpoints de autenticación.
    """
    
    AUTH_PATHS = ["/api/v1/bonus/calculate"]
    AUTH_FAILED_DETAIL = "Token inválido"
    
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method
        
        if method == "POST" and any(path.startswith(p) for p in self.AUTH_PATHS):
            client_ip = get_remote_address(request)
            
            is_blocked, remaining_time = failed_auth_tracker.is_blocked(client_ip)
            if is_blocked:
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": f"Demasiados intentos fallidos. Bloqueado por {remaining_time} segundos.",
                    },
                    headers={"Retry-After": str(remaining_time)},
                )
        
        return await call_next(request)


def check_rate_limit(ip: str, action: str = "default") -> tuple[bool, str]:
    """
    Función auxiliar para verificar rate limit programmatically.
    Útil para integrar en endpoints específicos.
    
    Returns:
        tuple: (is_allowed, message)
    """
    is_blocked, remaining_time = failed_auth_tracker.is_blocked(ip)
    
    if is_blocked:
        return False, f"Bloqueado. Intenta en {remaining_time} segundos."
    
    return True, ""


def record_auth_result(ip: str, success: bool, reason: str | None = None):
    """
    Registra el resultado de un intento de autenticación.
    Usado por el sistema de seguridad para trackear intentos fallidos.
    """
    if not success:
        is_blocked, remaining = failed_auth_tracker.record_failed_attempt(ip)
        logger.info(f"Auth fallido para IP {ip}: {remaining} intentos restantes")
    else:
        failed_auth_tracker.record_success(ip)