import io
import logging
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from app.models.schemas import ClientInfo

logger = logging.getLogger(__name__)

class PDFTemplateError(Exception):
    pass

# MAPPA DEL CLIENTE (Dati da Fatture in Cloud -> Campi PDF)
# Colleghiamo i dati anagrafici del cliente ai nomi dei campi nel tuo PDF
CLIENT_FIELD_MAP = {
    "commissionato da": "name",
    "comuneDI": "address_city",
    "in": "address_street",
}

# MAPPA EXTRA (Dati dal form web -> Campi PDF)
# Questi sono i campi che compili a mano nella web app
EXTRA_FIELD_MAP = {
    "esecutrice di": "descrizione_impianto",
    "inteso come": "tipo_intervento",
    "diProprietaDi": "proprietario",
    "adUso": "uso_edificio",
    "data": "data",
}

# MAPPA CHECKBOX (Allegati)
# Associa i nomi dei campi PDF (1, 2, 3...) alle checkbox del sito
ALLEGATI_MAP = {
    "allegato_progetto": "1",
    "allegato_relazione": "2",
    "allegato_schema": "3",
    "allegato_precedenti": "4",
    "allegato_certificato": "5",
    "allegato_conformita": "6",
    # Box di sicurezza (se presenti nel form)
    "sicurezza_materiali": "checkbox_15ltlf", 
    "sicurezza_controllo": "checkbox_17mewb",
}

def generate_declaration(
    client: ClientInfo,
    template_path: Path,
    extra_fields: dict[str, str] | None = None,
    allegati: dict[str, bool] | None = None,
) -> bytes:
    """Riempie il PDF con i soli dati variabili del cliente e dell'impianto."""
    if not template_path.exists():
        raise PDFTemplateError(f"Template PDF non trovato: {template_path}")

    reader = PdfReader(str(template_path))
    writer = PdfWriter()
    writer.append(reader)

    # Dizionario che conterrà i valori da scrivere
    values: dict[str, str] = {}

    # 1. Inserimento dati cliente da Fatture in Cloud
    client_dict = client.model_dump()
    for pdf_field, client_attr in CLIENT_FIELD_MAP.items():
        val = client_dict.get(client_attr)
        if val:
            values[pdf_field] = str(val)

    # 2. Inserimento dati variabili dal form (descrizione, data, ecc.)
    if extra_fields:
        for pdf_field, extra_key in EXTRA_FIELD_MAP.items():
            if extra_key in extra_fields and extra_fields[extra_key]:
                values[pdf_field] = str(extra_fields[extra_key])

    # 3. Gestione Checkbox degli allegati
    if allegati:
        for chiave_interna, nome_pdf in ALLEGATI_MAP.items():
            if allegati.get(chiave_interna):
                values[nome_pdf] = "/Yes"
            else:
                values[nome_pdf] = "/Off"

    # Applicazione dei valori ai campi AcroForm del PDF
    for page in writer.pages:
        writer.update_page_form_field_values(page, values, auto_regenerate=False)

    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()
