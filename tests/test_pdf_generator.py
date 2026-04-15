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
    assert "ragione_sociale" in fields
    assert "partita_iva" in fields
    assert "codice_fiscale" in fields


def test_get_template_fields_missing_file(tmp_path: Path):
    missing = tmp_path / "nope.pdf"
    with pytest.raises(PDFTemplateError):
        get_template_fields(missing)


def test_generate_declaration_fills_fields(sample_template_pdf: Path, sample_client):
    pdf_bytes = generate_declaration(
        client=sample_client,
        template_path=sample_template_pdf,
        extra_fields={"declaration_date": "15/04/2026", "declaration_number": "001/2026"},
    )
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0

    import io
    reader = PdfReader(io.BytesIO(pdf_bytes))
    fields = reader.get_fields()
    # Values should be filled
    assert fields["ragione_sociale"]["/V"] == "Mario Rossi SRL"
    assert fields["partita_iva"]["/V"] == "IT01234567890"
    assert fields["codice_fiscale"]["/V"] == "RSSMRA80A01H501U"
    assert fields["citta"]["/V"] == "Roma"
    assert fields["data_dichiarazione"]["/V"] == "15/04/2026"
    assert fields["numero_dichiarazione"]["/V"] == "001/2026"


def test_generate_declaration_missing_template(tmp_path: Path, sample_client):
    missing = tmp_path / "missing.pdf"
    with pytest.raises(PDFTemplateError):
        generate_declaration(client=sample_client, template_path=missing)
