import io
import logging
from pathlib import Path

from pypdf import PdfReader, PdfWriter

from app.models.schemas import ClientInfo

logger = logging.getLogger(__name__)

# Mappatura campi testo PDF → attributi ClientInfo.
CLIENT_FIELD_MAP: dict[str, str] = {
    "commissionato da": "name",
    "comuneDI": "address_city",
    "in": "address_street",
}

# Campi testo aggiuntivi passati come extra_fields.
EXTRA_FIELD_MAP: dict[str, str] = {
    "esecutrice di": "tipo_impianto",
    "inteso come": "descrizione_impianto",
    "diProprietaDi": "proprietario",
    "adUso": "uso_edificio",
    "data": "data",
    "comuneDI": "comune_installazione",
    "in": "via_installazione",
}

# Mappatura Checkbox diventati campi di testo (Nome nell'App -> Nome nel PDF)
CHECKBOX_MAP: dict[str, str] = {
    "dichiara_norma": "tick1",
    "dichiara_componenti": "tick2",
    "dichiara_controllo": "tick3",
    "allegato_progetto": "tick4",
    "allegato_relazione": "tick5",
    "allegato_schema": "tick6",
    "allegato_precedenti": "tick7",
    "allegato_certificato": "tick8",
    "allegato_conformita": "tick9",
}


class PDFTemplateError(Exception):
    pass


def get_template_fields(template_path: Path) -> list[str]:
    """Return the list of AcroForm field names found in the template PDF."""
    if not template_path.exists():
        raise PDFTemplateError(f"Template PDF non trovato: {template_path}")
    reader = PdfReader(str(template_path))
    fields = reader.get_fields()
    return list(fields.keys()) if fields else []


def generate_declaration(
    client: ClientInfo,
    template_path: Path,
    extra_fields: dict[str, str] | None = None,
    allegati: dict[str, bool] | None = None,
) -> bytes:
    """Fill the PDF template with client data and return the PDF bytes."""
    if not template_path.exists():
        raise PDFTemplateError(f"Template PDF non trovato: {template_path}")

    reader = PdfReader(str(template_path))
    writer = PdfWriter()
    writer.append(reader)

    # Recuperiamo i campi esistenti nel PDF per il debug
    pdf_fields = reader.get_fields() or {}

    # ── Text fields ────────────────────────────────────────────────────────
    text_values: dict[str, str] = {}

    client_dict = client.model_dump()
    for pdf_field, attr in CLIENT_FIELD_MAP.items():
        val = client_dict.get(attr)
        if val:
            text_values[pdf_field] = str(val)

    # proprietario defaults to client name when not provided
    text_values["proprietario"] = client.name

    # Extra fields override (including installation address override)
    if extra_fields:
        for pdf_field, extra_key in EXTRA_FIELD_MAP.items():
            val = extra_fields.get(extra_key)
            if val:
                text_values[pdf_field] = str(val)

    # ── "Checkboxes" (ora trattati come campi di testo) ────────────────────
    if allegati:
        logger.info(f"DEBUG PDF: Ricevuti allegati dal frontend: {allegati}")
        for app_name, pdf_name in CHECKBOX_MAP.items():
            # Controlliamo se il campo testo esiste davvero nel template PDF
            if pdf_name not in pdf_fields:
                logger.warning(f"DEBUG PDF: Il campo '{pdf_name}' NON ESISTE nel PDF! Controlla come lo hai chiamato.")
            
            # Se l'utente ha spuntato la voce nell'app, scriviamo "X", altrimenti vuoto
            if allegati.get(app_name, False):
                text_values[pdf_name] = "X"
                logger.info(f"DEBUG PDF: Scrivo 'X' nel campo '{pdf_name}' (associato a '{app_name}')")
            else:
                text_values[pdf_name] = ""

    # Compila in un colpo solo tutti i testi (inclusi i tick convertiti in X)
    for page in writer.pages:
        # Impostato auto_regenerate=True per forzare la visualizzazione delle X nei visualizzatori PDF
        writer.update_page_form_field_values(page, text_values, auto_regenerate=True)

    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()
