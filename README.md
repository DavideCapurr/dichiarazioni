# Dichiarazioni di Conformità

Web app per automatizzare la creazione delle **Dichiarazioni di Conformità dell'Impianto alla Regola d'Arte** (D.M. 22.1.2008 n.37) per **ITB Impianti Idraulici** (Davide Beccalossi), con integrazione **Fatture in Cloud**, compilazione di un template Word reale e esportazione PDF lato server.

## Funzionalità

- Ricerca clienti su Fatture in Cloud tramite ragione sociale
- Recupero automatico di P.IVA, codice fiscale, indirizzo, ecc.
- Compilazione del template DOCX con:
  - Dati cliente da Fatture in Cloud
  - Dati specifici della dichiarazione (tipo impianto, descrizione, proprietario, uso edificio)
  - Tick degli allegati e delle dichiarazioni come marker Word
  - Data e sezione firma
- Indirizzo di installazione precompilato dal cliente (modificabile)
- Esportazione PDF sempre sul backend, quindi il download funziona da qualsiasi dispositivo client

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
   DOCX_TEMPLATE_PATH=docx_templates/dichiarazione.docx
   ```

3. Il DOCX `docx_templates/dichiarazione.docx` è la fonte ufficiale del layout. Il backend lo modifica come documento Word e poi lo esporta in PDF.

4. Installa un converter DOCX -> PDF sul backend. In produzione è consigliato LibreOffice headless:

   ```bash
   # macOS
   brew install --cask libreoffice

   # Debian/Ubuntu server
   sudo apt-get update && sudo apt-get install -y libreoffice-writer
   ```

   Su macOS locale, se LibreOffice non è disponibile, l'app può usare Pages.app come fallback. I dispositivi degli utenti non devono avere nulla installato: la conversione avviene sul server.

   Verifica il converter:

   ```bash
   poetry run python scripts/check_pdf_converter.py
   ```

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

## Dati inseriti nel DOCX

Il generatore usa questi dati per modificare il template Word prima dell'esportazione PDF:

| Dato                 | Tipo     | Origine                                  |
|----------------------|----------|------------------------------------------|
| `commissionato_da`   | testo    | `client.name` (Fatture in Cloud)         |
| `comune_installazione` | testo  | `client.address_city` (override in UI)   |
| `via_installazione`  | testo    | `client.address_street` (override in UI) |
| `tipo_impianto`      | testo    | Input UI (es. "nuovo impianto idraulico")|
| `descrizione_impianto` | testo  | Input UI                                 |
| `proprietario`       | testo    | Input UI                                 |
| `uso_edificio`       | testo    | Input UI (es. "civile")                  |
| `data`               | testo    | Data dichiarazione (default: oggi)       |
| allegati             | tick     | Marker Word spuntati/non spuntati        |

## Modificare il layout

Se devi cambiare layout, font, spaziature o dati fissi, modifica `docx_templates/dichiarazione.docx`.

Per generare un DOCX compilato e il relativo PDF di esempio:

```bash
poetry run python scripts/build_template.py
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
│   │   └── pdf_generator.py    # Compilazione DOCX + export PDF
│   ├── models/schemas.py    # Schemi Pydantic
│   ├── templates/           # HTML (Jinja2)
│   └── static/              # CSS + JS
├── docx_templates/
│   └── dichiarazione.docx            # Template Word ufficiale
├── pdf_templates/
│   └── dichiarazione.pdf             # Template PDF legacy
├── scripts/
│   ├── build_template.py              # Genera DOCX/PDF di esempio
│   ├── check_pdf_converter.py         # Verifica export PDF lato server
│   └── inspect_pdf_fields.py          # Utility legacy AcroForm
└── tests/
```
