from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import ClientInfo

client = TestClient(app)


def test_generate_returns_pdf(sample_template_pdf: Path, sample_client: ClientInfo):
    from app.services import pdf_generator

    def fake_converter(docx_path: Path, output_dir: Path) -> bytes:
        return b"%PDF-1.4\n%%EOF"

    with patch("app.routers.declarations.get_client", return_value=sample_client), \
         patch("app.routers.declarations.settings") as mock_settings, \
         patch.object(pdf_generator, "_convert_docx_to_pdf", side_effect=fake_converter):
        mock_settings.docx_template_abs_path = sample_template_pdf
        response = client.post("/api/declarations/generate", json={
            "client_id": sample_client.id,
            "declaration_date": "2026-04-15",
            "tipo_impianto": "nuovo impianto idraulico",
            "uso_edificio": "civile",
            "allegati": {
                "dichiara_norma": True,
                "allegato_progetto": True,
                "allegato_certificato": True,
            },
        })

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment" in response.headers["content-disposition"]
    assert response.content.startswith(b"%PDF")


def test_generate_minimal(sample_template_pdf: Path, sample_client: ClientInfo):
    """Minimal request — date defaults to today, allegati default pre-checked."""
    from app.services import pdf_generator

    with patch("app.routers.declarations.get_client", return_value=sample_client), \
         patch("app.routers.declarations.settings") as mock_settings, \
         patch.object(pdf_generator, "_convert_docx_to_pdf", return_value=b"%PDF-1.4\n%%EOF"):
        mock_settings.docx_template_abs_path = sample_template_pdf
        response = client.post("/api/declarations/generate",
                               json={"client_id": sample_client.id})
    assert response.status_code == 200


def test_generate_not_found():
    from app.services.fattureincloud import FattureInCloudNotFoundError
    with patch("app.routers.declarations.get_client",
               side_effect=FattureInCloudNotFoundError("non trovato")):
        response = client.post("/api/declarations/generate", json={"client_id": 99999})
    assert response.status_code == 404
