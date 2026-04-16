import os
from pathlib import Path

import pytest

os.environ.setdefault("FIC_ACCESS_TOKEN", "test_token")
os.environ.setdefault("FIC_COMPANY_ID", "12345")


def _build_sample_pdf(path: Path) -> None:
    """Build a minimal PDF with all 17 AcroForm fields used by the app."""
    from reportlab.pdfgen import canvas as rl_canvas

    c = rl_canvas.Canvas(str(path))
    text_fields = [
        "tipo_impianto", "descrizione_impianto", "commissionato_da",
        "comune_installazione", "via_installazione", "proprietario",
        "uso_edificio", "data",
    ]
    checkboxes_off = ["dichiara_norma", "dichiara_componenti", "dichiara_controllo"]
    checkboxes_on = [
        "allegato_progetto", "allegato_relazione", "allegato_schema",
        "allegato_precedenti", "allegato_certificato", "allegato_conformita",
    ]
    y = 800
    for name in text_fields:
        c.acroForm.textfield(name=name, x=100, y=y, width=200, height=14,
                             borderStyle="underlined")
        y -= 20
    for name in checkboxes_off:
        c.acroForm.checkbox(name=name, x=100, y=y, size=10, checked=False)
        y -= 20
    for name in checkboxes_on:
        c.acroForm.checkbox(name=name, x=100, y=y, size=10, checked=True)
        y -= 20
    c.showPage()
    c.save()


@pytest.fixture
def sample_template_pdf(tmp_path: Path) -> Path:
    path = tmp_path / "sample_template.pdf"
    _build_sample_pdf(path)
    return path


@pytest.fixture
def sample_client():
    from app.models.schemas import ClientInfo

    return ClientInfo(
        id=42, name="Mario Rossi SRL", vat_number="IT01234567890",
        tax_code="RSSMRA80A01H501U", email="info@mariorossi.it",
        phone="+39 06 12345678", address_street="Via Roma 1",
        address_postal_code="00100", address_city="Roma", address_province="RM",
    )
