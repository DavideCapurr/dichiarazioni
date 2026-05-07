import os
from pathlib import Path

import pytest

os.environ.setdefault("FIC_ACCESS_TOKEN", "test_token")
os.environ.setdefault("FIC_COMPANY_ID", "12345")


@pytest.fixture
def sample_template_docx() -> Path:
    return Path(__file__).resolve().parent.parent / "docx_templates" / "dichiarazione.docx"


@pytest.fixture
def sample_template_pdf(sample_template_docx: Path) -> Path:
    """Backward-compatible fixture name used by declaration endpoint tests."""
    return sample_template_docx


@pytest.fixture
def sample_client():
    from app.models.schemas import ClientInfo

    return ClientInfo(
        id=42, name="Mario Rossi SRL", vat_number="IT01234567890",
        tax_code="RSSMRA80A01H501U", email="info@mariorossi.it",
        phone="+39 06 12345678", address_street="Via Roma 1",
        address_postal_code="00100", address_city="Roma", address_province="RM",
    )
