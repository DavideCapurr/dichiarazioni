from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import ClientInfo

client = TestClient(app)


def test_search_clients_returns_results():
    fake_clients = [
        ClientInfo(id=1, name="Mario Rossi SRL", vat_number="IT01234567890", address_city="Roma"),
        ClientInfo(id=2, name="Rossi Edile", vat_number="IT09876543210", address_city="Milano"),
    ]
    with patch("app.routers.clients.search_clients", return_value=fake_clients):
        response = client.get("/api/clients?q=Rossi")
    assert response.status_code == 200
    data = response.json()
    assert len(data["clients"]) == 2
    assert data["clients"][0]["name"] == "Mario Rossi SRL"


def test_search_clients_empty_query_rejected():
    response = client.get("/api/clients?q=")
    assert response.status_code == 422


def test_get_client_detail_returns_client():
    fake_client = ClientInfo(id=42, name="Test Client", vat_number="IT00000000000")
    with patch("app.routers.clients.get_client", return_value=fake_client):
        response = client.get("/api/clients/42")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 42
    assert data["name"] == "Test Client"


def test_auth_error_handler_returns_401():
    from app.services.fattureincloud import FattureInCloudAuthError

    def _raise(*args, **kwargs):
        raise FattureInCloudAuthError("Token non valido")

    with patch("app.routers.clients.search_clients", side_effect=_raise):
        response = client.get("/api/clients?q=test")
    assert response.status_code == 401
    assert "Token" in response.json()["error"]
