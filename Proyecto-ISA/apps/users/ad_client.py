import logging
import time
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class ISAClient:
    """Cliente HTTP para consumir la API de ISA (Active Directory + SIARE)."""

    def __init__(self):
        self.base_url = settings.ISA_API_URL
        self.client_id = settings.ISA_CLIENT_ID
        self.client_secret = settings.ISA_CLIENT_SECRET
        self._token = None
        self._token_expires_at = 0
        self.timeout = 10

    def _get_token(self):
        if self._token and time.time() < self._token_expires_at:
            return self._token
        try:
            resp = requests.post(
                f'{self.base_url}/api/auth/token',
                json={'clientId': self.client_id, 'clientSecret': self.client_secret},
                timeout=self.timeout
            )
            resp.raise_for_status()
            data = resp.json()
            self._token = data['accessToken']
            self._token_expires_at = time.time() + data['expiresIn'] - 60
            return self._token
        except requests.RequestException as e:
            logger.error(f'Error obteniendo token ISA: {e}')
            return None

    def validar_acceso(self, username, password):
        """Valida credenciales contra AD. Retorna dict o None si hay error de conexión."""
        token = self._get_token()
        if not token:
            return None
        try:
            resp = requests.post(
                f'{self.base_url}/api/active-directory/validar-acceso',
                headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
                json={'userName': username, 'password': password},
                timeout=self.timeout
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logger.error(f'Error validando acceso AD: {e}')
            return None

    def consultar_persona(self, username):
        """Consulta datos del usuario en vListaPersonasSiare. Retorna dict o None."""
        token = self._get_token()
        if not token:
            return None
        try:
            resp = requests.post(
                f'{self.base_url}/api/personas-siare/consultar-por-usuario-ad',
                headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
                json={'userName': username},
                timeout=self.timeout
            )
            resp.raise_for_status()
            data = resp.json()
            return data[0] if data else None
        except requests.RequestException as e:
            logger.error(f'Error consultando persona SIARE: {e}')
            return None
