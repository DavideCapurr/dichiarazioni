#!/usr/bin/env python3
"""
Utility script to inspect AcroForm field names in a PDF template.

Usage:
    python scripts/inspect_pdf_fields.py <path_to_pdf>

This helps you discover the exact names of the fillable fields in your
PDF template so you can update FIELD_MAP in app/services/pdf_generator.py.
"""
import sys
from pathlib import Path

from pypdf import PdfReader


def main():
    if len(sys.argv) != 2:
        print("Uso: python scripts/inspect_pdf_fields.py <path_to_pdf>")
        sys.exit(1)

    pdf_path = Path(sys.argv[1])
    if not pdf_path.exists():
        print(f"File non trovato: {pdf_path}")
        sys.exit(1)

    reader = PdfReader(str(pdf_path))
    fields = reader.get_fields()

    if not fields:
        print("Nessun campo AcroForm trovato nel PDF.")
        print("Assicurati che il template abbia campi compilabili.")
        sys.exit(0)

    print(f"Campi AcroForm trovati in {pdf_path.name}:")
    print("-" * 60)
    for name, field in fields.items():
        field_type = field.get("/FT", "?")
        current_value = field.get("/V", "")
        print(f"  {name!r:<40} tipo={field_type} valore={current_value!r}")
    print("-" * 60)
    print(f"Totale campi: {len(fields)}")
    print()
    print("Copia questi nomi in FIELD_MAP in app/services/pdf_generator.py")


if __name__ == "__main__":
    main()
