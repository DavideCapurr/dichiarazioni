from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import ClientInfo

client = TestClient(app)


def test_generate_declaration_returns_pdf(sample_template_pdf: Path, sample_client: ClientInfo):
    with patch("app.routers.declarations.get_client", return_value=sample_client), \
         patch("app.routers.declarations.settings") as mock_settings:
        mock_settings.pdf_template_abs_path = sample_template_pdf
        response = client.post(
            "/api/declarations/generate",
            json={
                "client_id": sample_client.id,
                "declaration_date": "2026-04-15",
                "tipo_impianto": "nuovo impianto idraulico",
                "uso_edificio": "civile",
                "allegati": {"allegato_certificato": True},
            },
        )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment" in response.headers["content-disposition"]
    assert "Mario_Rossi_SRL" in response.headers["content-disposition"]
    assert response.content.startswith(b"%PDF")


def test_generate_declaration_not_found(sample_template_pdf: Path):
    from app.services.fattureincloud import FattureInCloudNotFoundError

    def _raise(*args, **kwargs):
        raise FattureInCloudNotFoundError("Cliente non trovato")

    with patch("app.routers.declarations.get_client", side_effect=_raise):
        response = client.post(
            "/api/declarations/generate",
            json={"client_id": 99999},
        )
    assert response.status_code == 404


def test_generate_declaration_with_defaults(sample_template_pdf: Path, sample_client: ClientInfo):
    """Minimal request should work — date defaults to today, allegati default to false."""
    with patch("app.routers.declarations.get_client", return_value=sample_client), \
         patch("app.routers.declarations.settings") as mock_settings:
        mock_settings.pdf_template_abs_path = sample_template_pdf
        response = client.post(
            "/api/declarations/generate",
            json={"client_id": sample_client.id},
        )
    assert response.status_code == 200
