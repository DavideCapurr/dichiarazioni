# Dichiarazioni di Conformità

Web app per automatizzare la creazione delle **Dichiarazioni di Conformità dell'Impianto alla Regola d'Arte** (D.M. 22.1.2008 n.37) per **ITB Impianti Idraulici** (Davide Beccalossi), con integrazione **Fatture in Cloud** e compilazione automatica di un template PDF con campi AcroForm.

## Funzionalità

- Ricerca clienti su Fatture in Cloud tramite ragione sociale
- Recupero automatico di P.IVA, codice fiscale, indirizzo, ecc.
- Compilazione automatica del template PDF con:
  - Dati cliente da Fatture in Cloud
  - Dati specifici della dichiarazione (tipo impianto, descrizione, proprietario, uso edificio)
  - Checkbox per gli allegati obbligatori
- Indirizzo di installazione precompilato dal cliente (modificabile)
- Download immediato del PDF compilato

## Installazione

1. Clona il repository e installa le dipendenze con Poetry:

   ```bash
   poetry install
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

3. Il template PDF `pdf_templates/dichiarazione_conformita.pdf` è già incluso nel repo (generato con lo script `scripts/build_template.py`). Contiene:
   - **Dati fissi** di ITB Impianti Idraulici (P.IVA, indirizzo, CCIAA, albo artigiani)
   - **Campi AcroForm compilabili** per le parti variabili

## Avvio

```bash
poetry run uvicorn app.main:app --reload
```

Apri `http://localhost:8000` nel browser.

API docs: `http://localhost:8000/docs`

## Test

```bash
poetry run pytest tests/ -v
```

## Campi del template PDF

Il template ha 14 campi AcroForm:

| Campo                | Tipo     | Origine                                  |
|----------------------|----------|------------------------------------------|
| `commissionato_da`   | testo    | `client.name` (Fatture in Cloud)         |
| `comune_installazione` | testo  | `client.address_city` (override in UI)   |
| `via_installazione`  | testo    | `client.address_street` (override in UI) |
| `tipo_impianto`      | testo    | Input UI (es. "nuovo impianto idraulico")|
| `descrizione_impianto` | testo  | Input UI                                 |
| `proprietario`       | testo    | Input UI                                 |
| `uso_edificio`       | testo    | Input UI (es. "civile")                  |
| `data`               | testo    | Data dichiarazione (default: oggi)       |
| `allegato_progetto`  | checkbox | Checkbox UI                              |
| `allegato_relazione` | checkbox | Checkbox UI                              |
| `allegato_schema`    | checkbox | Checkbox UI                              |
| `allegato_precedenti`| checkbox | Checkbox UI                              |
| `allegato_certificato` | checkbox | Checkbox UI (default: spuntato)        |
| `allegato_conformita`| checkbox | Checkbox UI                              |

## Modificare il template

Se devi cambiare il layout o i dati fissi, modifica `scripts/build_template.py` e rigenera:

```bash
poetry run python scripts/build_template.py
```

Per ispezionare i campi AcroForm di un PDF:

```bash
poetry run python scripts/inspect_pdf_fields.py pdf_templates/dichiarazione_conformita.pdf
```

## Struttura del progetto

```
dichiarazioni/
├── app/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings da .env
│   ├── routers/             # Endpoint API
│   ├── services/
│   │   ├── fattureincloud.py   # Wrapper SDK FIC
│   │   └── pdf_generator.py    # Riempimento AcroForm
│   ├── models/schemas.py    # Schemi Pydantic
│   ├── templates/           # HTML (Jinja2)
│   └── static/              # CSS + JS
├── pdf_templates/
│   ├── dichiarazione_conformita.pdf  # Template con AcroForm (generato)
│   └── dichiarazione.pdf              # PDF di esempio/riferimento
├── scripts/
│   ├── build_template.py              # Rigenera il template
│   └── inspect_pdf_fields.py          # Ispeziona i campi
└── tests/
```
