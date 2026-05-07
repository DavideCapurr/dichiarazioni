#!/usr/bin/env python3
"""
Utility script to inspect legacy AcroForm field names in a PDF.

Usage:
    python scripts/inspect_pdf_fields.py <path_to_pdf>

The application now renders final PDFs as physical content, so generated
declarations should normally report no AcroForm fields.
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
        print("Questo e il risultato atteso per i PDF fisici generati dall'app.")
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
    print("Nota: questi campi sono legacy; il generatore principale non li compila piu.")


if __name__ == "__main__":
    main()
