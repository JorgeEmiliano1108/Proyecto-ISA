# tests/e2e/test_health.py
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

# Configuración obligatoria para usar asyncio en pytest
pytestmark = pytest.mark.asyncio

async def test_health_check_returns_200():
    """
    Smoke test: Verifica que el microservicio arranca y el Global Exception Handler
    no está bloqueando las rutas públicas.
    """
    # Usamos ASGITransport para probar la app en memoria sin levantar un puerto real
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        response = await ac.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "environment" in data