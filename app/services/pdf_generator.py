import io
import logging
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from app.models.schemas import ClientInfo

logger = logging.getLogger(__name__)

class PDFTemplateError(Exception):
    pass

# DATI AZIENDALI FISSI
# Verranno inseriti automaticamente in ogni nuovo PDF
DATI_FISSI_AZIENDA = {
    "Il Sottoscritto": "Davide Mario Beccalossi",
    "titolare o legale rappresentante dellimpresa": "ITB Impianti Idraulici di Beccalossi Davide Mario",
    "operante nel settore": "impianti idraulici",
    "con sede in via": "Della Rocchetta, 26",
    "Comune": "Brescia",
    "prov": "BS",
    "tel": "3480650844",
    "PIVA": "02269030983",
    "Iscritta RI": "/Yes",  # Spunta la checkbox Camera di Commercio
    "iscritta nel registro delle ditte DPR 07121995 n 581 della camera CIAA di": "Brescia",
    "n_2": "BCCDDM79M14B157C",
    "Iscritta Albo": "/Yes", # Spunta la checkbox Albo Artigiani
    "iscritta allAlbo Provinciale delle Imprese Artigiane L 881985 n 443 di": "Brescia",
    "n_3": "140291",
    # Spuntiamo in automatico anche i controlli di sicurezza in basso
    "installato componenti e materiali adatti al luogo di installazione": "/Yes",
    "controllato": "/Yes",
}

# MAPPA DEL CLIENTE (Da Fatture In Cloud)
CLIENT_FIELD_MAP = {
    "Commissionato da": "name",
    "Installato nei locali siti nel Comune di": "address_city",
    "prov_2": "address_province",
    "Via": "address_street",
}

# MAPPA EXTRA (Dai campi compilati a mano sul sito web)
EXTRA_FIELD_MAP = {
    "Esecutrice dellimpianto 2 1": "descrizione_impianto",
    "n_4": "civico_installazione",
    "scala": "scala_installazione",
    "piano": "piano_installazione",
    "Interno": "interno_installazione",
    "di proprietà di": "proprietario",
    "Data": "data",
}

# MAPPA ALLEGATI (Checkbox finali)
ALLEGATI_MAP = {
    "allegato_progetto": "progetto ai sensi dellart 5 e 75",
    "allegato_relazione": "relazione con tipologie dei materiali utilizzati 6",
    "allegato_schema": "schema di impianto realizzato 7",
    "allegato_precedenti": "riferimento a dichiarazioni di conformità precedenti o parziali già esistenti8",
    "allegato_certificato": "copia del certificato di riconoscimento dei requisiti tecnicoprofessionali",
    "allegato_conformita": "attestazione di conformità per impianto realizzato con materiali o sistemi non normalizzati 9",
}

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

    # 1. Popoliamo con i dati aziendali
    values: dict[str, str] = DATI_FISSI_AZIENDA.copy()

    # 2. Dati del cliente
    client_dict = client.model_dump()
    for pdf_field, client_attr in CLIENT_FIELD_MAP.items():
        val = client_dict.get(client_attr)
        if val is not None:
            values[pdf_field] = str(val)

    # 3. Campi extra e indirizzo inserito manualmente
    if extra_fields:
        for pdf_field, extra_key in EXTRA_FIELD_MAP.items():
            if extra_key in extra_fields and extra_fields[extra_key]:
                values[pdf_field] = str(extra_fields[extra_key])
        
        for pdf_field in CLIENT_FIELD_MAP.keys():
            # Gestiamo il caso in cui vogliamo sovrascrivere l'indirizzo
            chiave_html = CLIENT_FIELD_MAP[pdf_field]
            # Mappiamo le chiavi HTML ai nomi usati in extra_fields
            html_to_extra = {
                "name": "commissionato_da",
                "address_city": "comune_installazione",
                "address_province": "prov_installazione",
                "address_street": "via_installazione"
            }
            extra_chiave = html_to_extra.get(chiave_html)
            if extra_chiave and extra_chiave in extra_fields and extra_fields[extra_chiave]:
                values[pdf_field] = str(extra_fields[extra_chiave])

        # GESTIONE RADIO BUTTONS (Menu a tendina)
        # Nota: I PDF a volte richiedono valori come '/1', '/2' o il nome esatto dell'opzione
        # Passiamo direttamente il testo sperando che chi ha fatto il PDF abbia usato nomi logici
        tipo_int = extra_fields.get("tipo_intervento")
        if tipo_int:
            # Aggiunge lo slash necessario per le variabili AcroForm (es: /nuovo impianto)
            values["Inteso come"] = f"/{tipo_int}"

        uso_ed = extra_fields.get("uso_edificio")
        if uso_ed:
            values["In edificio adibito ad uso"] = f"/{uso_ed}"

    # 4. Checkbox degli allegati
    if allegati:
        for chiave_interna, nome_pdf in ALLEGATI_MAP.items():
            if allegati.get(chiave_interna):
                values[nome_pdf] = "/Yes"
            else:
                values[nome_pdf] = "/Off"

    # Scrive i dati sul PDF
    for page in writer.pages:
        writer.update_page_form_field_values(page, values, auto_regenerate=False)

    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()
