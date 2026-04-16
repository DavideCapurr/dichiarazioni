import io
from pathlib import Path

import pytest
from pypdf import PdfReader

from app.services.pdf_generator import (
    PDFTemplateError,
    generate_declaration,
    get_template_fields,
)


def test_get_template_fields(sample_template_pdf: Path):
    fields = get_template_fields(sample_template_pdf)
    assert "commissionato_da" in fields
    assert "dichiara_norma" in fields
    assert "allegato_certificato" in fields
    assert "data" in fields


def test_missing_template(tmp_path: Path):
    with pytest.raises(PDFTemplateError):
        get_template_fields(tmp_path / "nope.pdf")


def test_text_fields_filled(sample_template_pdf: Path, sample_client):
    extra = {"data": "15/04/2026", "tipo_impianto": "nuovo impianto idraulico",
              "uso_edificio": "civile"}
    pdf_bytes = generate_declaration(sample_client, sample_template_pdf, extra)
    reader = PdfReader(io.BytesIO(pdf_bytes))
    fields = reader.get_fields()
    assert fields["commissionato_da"]["/V"] == "Mario Rossi SRL"
    assert fields["comune_installazione"]["/V"] == "Roma"
    assert fields["via_installazione"]["/V"] == "Via Roma 1"
    assert fields["proprietario"]["/V"] == "Mario Rossi SRL"  # defaults to client name
    assert fields["data"]["/V"] == "15/04/2026"


def test_proprietario_defaults_to_client_name(sample_template_pdf: Path, sample_client):
    pdf_bytes = generate_declaration(sample_client, sample_template_pdf)
    fields = PdfReader(io.BytesIO(pdf_bytes)).get_fields()
    assert fields["proprietario"]["/V"] == "Mario Rossi SRL"


def test_proprietario_override(sample_template_pdf: Path, sample_client):
    pdf_bytes = generate_declaration(
        sample_client, sample_template_pdf, extra_fields={"proprietario": "Sig. Bianchi"}
    )
    fields = PdfReader(io.BytesIO(pdf_bytes)).get_fields()
    assert fields["proprietario"]["/V"] == "Sig. Bianchi"


def test_installation_address_override(sample_template_pdf: Path, sample_client):
    extra = {"comune_installazione": "Voghera", "via_installazione": "via Leopardi 11"}
    pdf_bytes = generate_declaration(sample_client, sample_template_pdf, extra)
    fields = PdfReader(io.BytesIO(pdf_bytes)).get_fields()
    assert fields["comune_installazione"]["/V"] == "Voghera"
    assert fields["via_installazione"]["/V"] == "via Leopardi 11"


def _get_checkbox_as(pdf_bytes: bytes, field_name: str) -> str:
    """Return the /AS value of a checkbox annotation."""
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(pdf_bytes))
    page = reader.pages[0]
    for ref in page.get("/Annots", []):
        annot = ref.get_object()
        if str(annot.get("/T", "")) == field_name:
            return str(annot.get("/AS", ""))
    return ""


def test_checkboxes_on(sample_template_pdf: Path, sample_client):
    allegati = {n: True for n in [
        "dichiara_norma", "dichiara_componenti", "dichiara_controllo",
        "allegato_progetto", "allegato_relazione", "allegato_schema",
        "allegato_precedenti", "allegato_certificato", "allegato_conformita",
    ]}
    pdf_bytes = generate_declaration(sample_client, sample_template_pdf, allegati=allegati)
    for name in allegati:
        assert _get_checkbox_as(pdf_bytes, name) == "/Yes", f"{name} not /Yes"


def test_checkboxes_off(sample_template_pdf: Path, sample_client):
    allegati = {n: False for n in [
        "dichiara_norma", "allegato_progetto", "allegato_certificato"
    ]}
    pdf_bytes = generate_declaration(sample_client, sample_template_pdf, allegati=allegati)
    for name in allegati:
        assert _get_checkbox_as(pdf_bytes, name) == "/Off", f"{name} not /Off"


def test_missing_template_generate(tmp_path: Path, sample_client):
    with pytest.raises(PDFTemplateError):
        generate_declaration(sample_client, tmp_path / "missing.pdf")
