#!/usr/bin/env python3
"""
Generate sample DOCX and PDF files from the Word template.

Usage:
    python scripts/build_template.py
"""
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.models.schemas import ClientInfo
from app.services.pdf_generator import generate_declaration, render_declaration_docx

TEMPLATE_PATH = BASE_DIR / "docx_templates" / "dichiarazione.docx"
DOCX_OUTPUT_PATH = BASE_DIR / "docx_templates" / "dichiarazione_compilata_sample.docx"
PDF_OUTPUT_PATH = BASE_DIR / "pdf_templates" / "dichiarazione_conformita_sample.pdf"


def build() -> None:
    client = ClientInfo(
        id=1,
        name="Mario Rossi SRL",
        vat_number="IT01234567890",
        tax_code="RSSMRA80A01H501U",
        address_street="Via Roma 1",
        address_postal_code="00100",
        address_city="Roma",
        address_province="RM",
    )
    extra_fields = {
        "data": "15/04/2026",
        "tipo_impianto": "nuovo impianto idraulico",
        "descrizione_impianto": "impianto idrico sanitario",
        "proprietario": "Sig. Mario Rossi",
        "uso_edificio": "civile",
    }
    allegati = {
        "dichiara_norma": True,
        "dichiara_componenti": True,
        "dichiara_controllo": True,
        "allegato_progetto": True,
        "allegato_relazione": True,
        "allegato_schema": True,
        "allegato_precedenti": False,
        "allegato_certificato": True,
        "allegato_conformita": False,
    }

    DOCX_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    PDF_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    DOCX_OUTPUT_PATH.write_bytes(
        render_declaration_docx(client, TEMPLATE_PATH, extra_fields, allegati)
    )
    PDF_OUTPUT_PATH.write_bytes(
        generate_declaration(client, TEMPLATE_PATH, extra_fields, allegati)
    )
    print(f"DOCX compilato generato: {DOCX_OUTPUT_PATH}")
    print(f"PDF esportato generato: {PDF_OUTPUT_PATH}")


if __name__ == "__main__":
    build()
