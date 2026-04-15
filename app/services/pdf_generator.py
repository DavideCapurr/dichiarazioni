import io
import logging
from datetime import date
from pathlib import Path

from pypdf import PdfReader, PdfWriter

from app.models.schemas import ClientInfo

logger = logging.getLogger(__name__)

# Maps PDF AcroForm field names -> ClientInfo attribute names.
# Adjust the keys to match the actual field names in your PDF template.
# Use scripts/inspect_pdf_fields.py to discover the field names.
FIELD_MAP: dict[str, str] = {
    "ragione_sociale": "name",
    "partita_iva": "vat_number",
    "codice_fiscale": "tax_code",
    "indirizzo": "address_street",
    "cap": "address_postal_code",
    "citta": "address_city",
    "provincia": "address_province",
    "email": "email",
    "telefono": "phone",
}

# Extra fields that are not from the client entity but added at generation time.
EXTRA_FIELD_MAP: dict[str, str] = {
    "data_dichiarazione": "declaration_date",
    "numero_dichiarazione": "declaration_number",
    "note": "notes",
}


class PDFTemplateError(Exception):
    pass


def get_template_fields(template_path: Path) -> list[str]:
    """Return the list of AcroForm field names found in the template PDF."""
    if not template_path.exists():
        raise PDFTemplateError(
            f"Template PDF non trovato: {template_path}"
        )
    reader = PdfReader(str(template_path))
    fields = reader.get_fields()
    if not fields:
        return []
    return list(fields.keys())


def generate_declaration(
    client: ClientInfo,
    template_path: Path,
    extra_fields: dict[str, str] | None = None,
) -> bytes:
    """Fill the PDF template with client data and return the resulting PDF bytes."""
    if not template_path.exists():
        raise PDFTemplateError(
            f"Template PDF non trovato: {template_path}"
        )

    reader = PdfReader(str(template_path))
    writer = PdfWriter()
    writer.append(reader)

    # Build the values dict: pdf_field_name -> value
    values: dict[str, str] = {}

    client_dict = client.model_dump()
    for pdf_field, client_attr in FIELD_MAP.items():
        val = client_dict.get(client_attr)
        if val is not None:
            values[pdf_field] = str(val)

    # Add extra fields (date, number, notes)
    if extra_fields:
        for pdf_field, extra_key in EXTRA_FIELD_MAP.items():
            val = extra_fields.get(extra_key)
            if val is not None:
                values[pdf_field] = str(val)

    if not values:
        logger.warning("Nessun valore da inserire nel PDF.")

    # Fill form fields on each page
    for page in writer.pages:
        writer.update_page_form_field_values(page, values, auto_regenerate=False)

    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()
