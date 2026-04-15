import io
from pathlib import Path

import pytest
from pypdf import PdfReader

from app.services.pdf_generator import (
    PDFTemplateError,
    generate_declaration,
    get_template_fields,
)


def test_get_template_fields_lists_acroform_names(sample_template_pdf: Path):
    fields = get_template_fields(sample_template_pdf)
    assert "commissionato_da" in fields
    assert "comune_installazione" in fields
    assert "via_installazione" in fields
    assert "data" in fields


def test_get_template_fields_missing_file(tmp_path: Path):
    missing = tmp_path / "nope.pdf"
    with pytest.raises(PDFTemplateError):
        get_template_fields(missing)


def test_generate_declaration_fills_client_and_extra(sample_template_pdf: Path, sample_client):
    extra = {
        "data": "15/04/2026",
        "tipo_impianto": "nuovo impianto idraulico",
        "descrizione_impianto": "impianto idrico sanitario",
        "proprietario": "Mario Bianchi",
        "uso_edificio": "civile",
    }
    pdf_bytes = generate_declaration(
        client=sample_client,
        template_path=sample_template_pdf,
        extra_fields=extra,
    )
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0

    reader = PdfReader(io.BytesIO(pdf_bytes))
    fields = reader.get_fields()
    # Client-mapped fields
    assert fields["commissionato_da"]["/V"] == "Mario Rossi SRL"
    assert fields["comune_installazione"]["/V"] == "Roma"  # from client
    assert fields["via_installazione"]["/V"] == "Via Roma 1"  # from client
    # Extra fields
    assert fields["data"]["/V"] == "15/04/2026"
    assert fields["tipo_impianto"]["/V"] == "nuovo impianto idraulico"
    assert fields["proprietario"]["/V"] == "Mario Bianchi"
    assert fields["uso_edificio"]["/V"] == "civile"


def test_extra_fields_override_client_address(sample_template_pdf: Path, sample_client):
    """When the user fills in a different installation address, it overrides client data."""
    extra = {
        "comune_installazione": "Voghera",
        "via_installazione": "via Leopardi 11",
    }
    pdf_bytes = generate_declaration(
        client=sample_client,
        template_path=sample_template_pdf,
        extra_fields=extra,
    )
    reader = PdfReader(io.BytesIO(pdf_bytes))
    fields = reader.get_fields()
    assert fields["comune_installazione"]["/V"] == "Voghera"
    assert fields["via_installazione"]["/V"] == "via Leopardi 11"


def test_allegati_checkboxes(sample_template_pdf: Path, sample_client):
    allegati = {
        "allegato_certificato": True,
        "allegato_progetto": False,
    }
    pdf_bytes = generate_declaration(
        client=sample_client,
        template_path=sample_template_pdf,
        allegati=allegati,
    )
    reader = PdfReader(io.BytesIO(pdf_bytes))
    fields = reader.get_fields()
    # Checked box should have value /Yes
    assert fields["allegato_certificato"]["/V"] in ("/Yes", "Yes")


def test_generate_declaration_missing_template(tmp_path: Path, sample_client):
    missing = tmp_path / "missing.pdf"
    with pytest.raises(PDFTemplateError):
        generate_declaration(client=sample_client, template_path=missing)
