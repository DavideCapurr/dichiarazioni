# Dichiarazioni di Conformità

Web app per automatizzare la creazione delle Dichiarazioni di Conformità per i clienti, con integrazione **Fatture in Cloud** e compilazione automatica di un template PDF con campi AcroForm.

## Funzionalità

- Ricerca clienti su Fatture in Cloud tramite ragione sociale
- Recupero automatico di P.IVA, codice fiscale, indirizzo, ecc.
- Compilazione automatica del template PDF della Dichiarazione di Conformità
- Download immediato del PDF compilato

## Installazione

1. Clona il repository e installa le dipendenze:

   ```bash
   pip install -r requirements.txt
   ```

2. Copia `.env.example` in `.env` e configura le credenziali:

   ```bash
   cp .env.example .env
   ```

   Modifica `.env`:

   ```
   FIC_ACCESS_TOKEN=il_tuo_token_privato
   FIC_COMPANY_ID=12345
   PDF_TEMPLATE_PATH=pdf_templates/dichiarazione_conformita.pdf
   ```

3. Posiziona il tuo template PDF (con campi AcroForm compilabili) in `pdf_templates/`.

## Configurazione dei campi PDF

Prima del primo utilizzo devi verificare che i nomi dei campi AcroForm nel tuo template corrispondano al mapping interno.

Usa lo script di ispezione:

```bash
python scripts/inspect_pdf_fields.py pdf_templates/dichiarazione_conformita.pdf
```

Quindi aggiorna `FIELD_MAP` in `app/services/pdf_generator.py` adattando le chiavi (nomi campi PDF) agli attributi del cliente.

Mapping di default:

| Campo PDF              | Attributo cliente     |
|------------------------|-----------------------|
| `ragione_sociale`      | `name`                |
| `partita_iva`          | `vat_number`          |
| `codice_fiscale`       | `tax_code`            |
| `indirizzo`            | `address_street`      |
| `cap`                  | `address_postal_code` |
| `citta`                | `address_city`        |
| `provincia`            | `address_province`    |
| `email`                | `email`               |
| `telefono`             | `phone`               |
| `data_dichiarazione`   | (generato)            |
| `numero_dichiarazione` | (generato)            |
| `note`                 | (generato)            |

## Avvio

```bash
uvicorn app.main:app --reload
```

Apri `http://localhost:8000` nel browser.

API docs: `http://localhost:8000/docs`

## Test

```bash
pytest tests/ -v
```

## Struttura del progetto

```
dichiarazioni/
├── app/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings da .env
│   ├── routers/             # Endpoint API
│   ├── services/            # Logica FIC e PDF
│   ├── models/              # Schemi Pydantic
│   ├── templates/           # index.html
│   └── static/              # CSS + JS
├── pdf_templates/           # Template PDF dell'utente
├── scripts/
│   └── inspect_pdf_fields.py
└── tests/
```
