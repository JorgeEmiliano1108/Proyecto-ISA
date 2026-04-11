# app/infrastructure/clients/user_service.py
import httpx
from fastapi import HTTPException, status

from app.application.ports.output import IUserServiceClient
from app.domain.entities import ActorRole

class UserServiceClient(IUserServiceClient):
    """
    Adaptador HTTP real para comunicarse con el Core HR System (Django).
    """
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=5.0)

    async def get_actor_role(self, actor_id: str) -> ActorRole:
        try:
            response = await self.client.get(f"/api/internal/users/{actor_id}/role")
            response.raise_for_status()
            
            data = response.json()
            return ActorRole(data["role"].upper())
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="Usuario no encontrado en el Directorio Activo.")
            raise HTTPException(status_code=502, detail="Error comunicándose con el servicio de usuarios.")
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="El servicio de usuarios no está disponible.")