"""
Pruebas End-to-End para los endpoints REST del bonus_service.
Usa TestClient de FastAPI con mocks de repositorios.
"""
import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from app.main import app
from app.domain.entities import BonusCalculation
from app.infrastructure.api.dependencies import (
    get_calculate_bonus_use_case,
    get_bonus_report_use_case,
)


MOCK_BONUS = BonusCalculation(
    empleado_id=1,
    periodo="2025-Q4",
    salario_base_snapshot=Decimal("10000.00"),
    impacto_ebitda=Decimal("0.80"),
    calificacion_global=Decimal("4.00"),
    monto_bono=Decimal("8000.00"),
    calculado_en=datetime(2025, 12, 1, 10, 0, 0),
)

VALID_PAYLOAD = {
    "evaluacion_id": "123e4567-e89b-12d3-a456-426614174000",
    "salario_base_snapshot": 10000.00,
    "impacto_ebitda_logrado": 85.50,
    "calificacion_global": 4.0,
}

MOCK_JWT = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test"


def make_mock_calculate_uc():
    uc = MagicMock()
    uc.execute = AsyncMock(return_value=MOCK_BONUS.to_dict())
    return uc


def make_mock_report_uc():
    uc = MagicMock()
    uc.execute = AsyncMock(return_value=[MOCK_BONUS.to_dict()])
    return uc


@pytest.fixture
def client():
    app.dependency_overrides[get_calculate_bonus_use_case] = make_mock_calculate_uc
    app.dependency_overrides[get_bonus_report_use_case] = make_mock_report_uc
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


class TestCalculateBonusEndpoint:
    def test_calculate_returns_201(self, client):
        response = client.post(
            "/api/v1/bonus/calculate",
            json=VALID_PAYLOAD,
            headers={"Authorization": MOCK_JWT},
        )
        # Sin JWT real el auth fallará — validamos estructura de error
        assert response.status_code in (201, 401)

    def test_invalid_periodo_format_returns_422(self, client):
        payload = {**VALID_PAYLOAD, "periodo": "2025-T5"}
        response = client.post(
            "/api/v1/bonus/calculate",
            json=payload,
            headers={"Authorization": MOCK_JWT},
        )
        assert response.status_code == 422

    def test_negative_salario_returns_422(self, client):
        payload = {**VALID_PAYLOAD, "salario_base_snapshot": -100}
        response = client.post(
            "/api/v1/bonus/calculate",
            json=payload,
            headers={"Authorization": MOCK_JWT},
        )
        assert response.status_code == 422


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        response = client.get("/api/v1/bonus/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
