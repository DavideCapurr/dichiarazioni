import io
import os
from pathlib import Path

import pytest

# Set required env vars before importing app modules
os.environ.setdefault("FIC_ACCESS_TOKEN", "test_token")
os.environ.setdefault("FIC_COMPANY_ID", "12345")


def _build_sample_pdf_with_fields(path: Path) -> None:
    """Build a minimal PDF with AcroForm fields using pypdf."""
    from pypdf import PdfWriter
    from pypdf.generic import (
        ArrayObject,
        BooleanObject,
        DictionaryObject,
        NameObject,
        RectangleObject,
        TextStringObject,
    )

    writer = PdfWriter()
    page = writer.add_blank_page(width=595, height=842)

    fields_to_create = [
        "ragione_sociale",
        "partita_iva",
        "codice_fiscale",
        "indirizzo",
        "cap",
        "citta",
        "provincia",
        "email",
        "telefono",
        "data_dichiarazione",
        "numero_dichiarazione",
        "note",
    ]

    annots = ArrayObject()
    y_top = 800
    for idx, field_name in enumerate(fields_to_create):
        y = y_top - (idx * 40)
        field = DictionaryObject({
            NameObject("/T"): TextStringObject(field_name),
            NameObject("/FT"): NameObject("/Tx"),
            NameObject("/V"): TextStringObject(""),
            NameObject("/Rect"): RectangleObject([100, y, 400, y + 20]),
            NameObject("/Subtype"): NameObject("/Widget"),
            NameObject("/Type"): NameObject("/Annot"),
            NameObject("/P"): page.indirect_reference,
        })
        field_ref = writer._add_object(field)
        annots.append(field_ref)

    page[NameObject("/Annots")] = annots

    acroform = DictionaryObject({
        NameObject("/Fields"): annots,
        NameObject("/NeedAppearances"): BooleanObject(True),
    })
    writer._root_object[NameObject("/AcroForm")] = acroform

    with open(path, "wb") as f:
        writer.write(f)


@pytest.fixture
def sample_template_pdf(tmp_path: Path) -> Path:
    path = tmp_path / "sample_template.pdf"
    _build_sample_pdf_with_fields(path)
    return path


@pytest.fixture
def sample_client():
    from app.models.schemas import ClientInfo

    return ClientInfo(
        id=42,
        name="Mario Rossi SRL",
        vat_number="IT01234567890",
        tax_code="RSSMRA80A01H501U",
        email="info@mariorossi.it",
        phone="+39 06 12345678",
        address_street="Via Roma 1",
        address_postal_code="00100",
        address_city="Roma",
        address_province="RM",
    )
