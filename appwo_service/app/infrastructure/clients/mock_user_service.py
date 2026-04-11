# app/infrastructure/clients/mock_user_service.py

# CORRECCIÓN: Viene de 'output', no de 'input'
from app.application.ports.output import IUserServiceClient
from app.domain.entities import ActorRole

class MockUserServiceClient(IUserServiceClient):
    """
    Adaptador Falso para pruebas locales.
    Simula la respuesta del Active Directory sin hacer peticiones de red.
    """
    async def get_actor_role(self, actor_id: str) -> ActorRole:
        print(f" [MOCK ACTIVO] Simulando rol MANAGER para el usuario {actor_id}")
        return ActorRole.MANAGER