import io
import logging
from pathlib import Path

from pypdf import PdfReader, PdfWriter

from app.models.schemas import ClientInfo

logger = logging.getLogger(__name__)

# Mappatura campi PDF -> attributi del cliente Fatture in Cloud.
# I valori qui saranno precompilati dai dati di FIC quando si seleziona un cliente.
CLIENT_FIELD_MAP: dict[str, str] = {
    "commissionato_da": "name",
    "comune_installazione": "address_city",
    "via_installazione": "address_street",
}

# Campi testuali aggiuntivi passati come extra_fields dalla UI.
# Chiave = nome campo PDF, valore = chiave nel dizionario extra_fields.
EXTRA_FIELD_MAP: dict[str, str] = {
    "tipo_impianto": "tipo_impianto",
    "descrizione_impianto": "descrizione_impianto",
    "proprietario": "proprietario",
    "uso_edificio": "uso_edificio",
    "data": "data",
}

# Nomi dei campi checkbox per gli allegati.
ALLEGATO_CHECKBOXES: list[str] = [
    "allegato_progetto",
    "allegato_relazione",
    "allegato_schema",
    "allegato_precedenti",
    "allegato_certificato",
    "allegato_conformita",
]


class PDFTemplateError(Exception):
    pass


def get_template_fields(template_path: Path) -> list[str]:
    """Return the list of AcroForm field names found in the template PDF."""
    if not template_path.exists():
        raise PDFTemplateError(f"Template PDF non trovato: {template_path}")
    reader = PdfReader(str(template_path))
    fields = reader.get_fields()
    if not fields:
        return []
    return list(fields.keys())


def generate_declaration(
    client: ClientInfo,
    template_path: Path,
    extra_fields: dict[str, str] | None = None,
    allegati: dict[str, bool] | None = None,
) -> bytes:
    """Fill the PDF template with client data and return the resulting PDF bytes."""
    if not template_path.exists():
        raise PDFTemplateError(f"Template PDF non trovato: {template_path}")

    reader = PdfReader(str(template_path))
    writer = PdfWriter()
    writer.append(reader)

    # Build text values
    values: dict[str, str] = {}

    client_dict = client.model_dump()
    for pdf_field, client_attr in CLIENT_FIELD_MAP.items():
        val = client_dict.get(client_attr)
        if val is not None:
            values[pdf_field] = str(val)

    # Extra fields override client defaults (e.g. user overrides
    # installation address even if defaulted from client address).
    if extra_fields:
        for pdf_field, extra_key in EXTRA_FIELD_MAP.items():
            val = extra_fields.get(extra_key)
            if val is not None and val != "":
                values[pdf_field] = str(val)
        # Also allow override of client-sourced fields (like comune/via) when
        # the extra_fields dict includes them directly by pdf_field name.
        for pdf_field in CLIENT_FIELD_MAP.keys():
            if pdf_field in extra_fields and extra_fields[pdf_field]:
                values[pdf_field] = str(extra_fields[pdf_field])

    # Checkboxes: set to /Yes for checked, /Off for unchecked
    if allegati:
        for cb_name in ALLEGATO_CHECKBOXES:
            if allegati.get(cb_name):
                values[cb_name] = "/Yes"
            else:
                values[cb_name] = "/Off"

    # Apply to each page
    for page in writer.pages:
        writer.update_page_form_field_values(page, values, auto_regenerate=False)

    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()
