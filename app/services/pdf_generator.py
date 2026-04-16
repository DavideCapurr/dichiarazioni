import io
import logging
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject

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

# Mappatura Checkbox (Nome nell'App -> Nome nel PDF)
CHECKBOX_MAP: dict[str, str] = {
    # 3 DICHIARA (Non obbligatori - l'app li imposta a False di default)
    "dichiara_norma": "1",
    "dichiara_componenti": "2",
    "dichiara_controllo": "3",
    
    # 6 ALLEGATI (Obbligatori - l'app li imposta a True di default)
    "allegato_progetto": "4",
    "allegato_relazione": "5",
    "allegato_schema": "6",
    "allegato_precedenti": "checkbox_15ltlf",
    "allegato_certificato": "checkbox_17mewb",
    "allegato_conformita": "9",
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


def _fill_checkboxes(writer: PdfWriter, checkbox_values: dict[str, bool]) -> None:
    """Directly update /V and /AS on every checkbox widget annotation.

    Some PDF viewers only look at /AS (Appearance State) to decide whether
    to render the tick; setting both /V and /AS ensures it works everywhere.
    """
    for page in writer.pages:
        annots = page.get("/Annots")
        if annots is None:
            continue
        for ref in annots:
            annot = ref.get_object()
            field_name = annot.get("/T")
            if field_name is None:
                continue
            name = str(field_name)
            if name not in checkbox_values:
                continue
            state = NameObject("/Yes") if checkbox_values[name] else NameObject("/Off")
            annot.update({
                NameObject("/V"): state,
                NameObject("/AS"): state,
            })


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

    for page in writer.pages:
        writer.update_page_form_field_values(page, text_values, auto_regenerate=False)

    # ── Checkboxes ─────────────────────────────────────────────────────────
    if allegati:
        cb_values = {name: bool(allegati.get(name, False)) for name in ALL_CHECKBOXES}
        _fill_checkboxes(writer, cb_values)

    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()
