#!/usr/bin/env python3
"""
Genera il template PDF della Dichiarazione di Conformità con campi AcroForm.
Dati fissi: ITB Impianti Idraulici / Davide Beccalossi.
Campi variabili: cliente, installazione, impianto + 9 checkbox (3 DICHIARA + 6 ALLEGATI).

Uso:
    python scripts/build_template.py
"""
from pathlib import Path

from reportlab.lib.colors import black, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN_LEFT = 2 * cm
MARGIN_RIGHT = 2 * cm
CONTENT_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT

OUTPUT_PATH = (
    Path(__file__).resolve().parent.parent
    / "pdf_templates"
    / "dichiarazione_conformita.pdf"
)


def para(c: canvas.Canvas, text: str, x: float, y: float, width: float,
         font: str = "Helvetica", size: int = 10, leading: float = 13,
         align: int = 0) -> float:
    """Draw a wrapped paragraph; return Y below it."""
    style = ParagraphStyle("p", fontName=font, fontSize=size,
                           leading=leading, alignment=align, textColor=black)
    p = Paragraph(text, style)
    _, h = p.wrap(width, 1000)
    p.drawOn(c, x, y - h)
    return y - h


def textfield(c: canvas.Canvas, name: str, x: float, y: float,
              width: float, height: float = 14, tooltip: str = "") -> None:
    c.acroForm.textfield(
        name=name, tooltip=tooltip or name,
        x=x, y=y, width=width, height=height,
        borderStyle="underlined", borderColor=black,
        fillColor=white, textColor=black,
        forceBorder=False, fontSize=9, fontName="Helvetica",
    )


def checkbox(c: canvas.Canvas, name: str, x: float, y: float,
             checked: bool = False, tooltip: str = "", size: float = 10) -> None:
    c.acroForm.checkbox(
        name=name, tooltip=tooltip or name,
        x=x, y=y, size=size,
        checked=checked,
        buttonStyle="check",
        borderColor=black, fillColor=white,
    )


def build(output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(output), pagesize=A4)
    c.setTitle("Dichiarazione di Conformita")

    # ── Header ──────────────────────────────────────────────────────────────
    c.setFont("Helvetica-Bold", 9)
    c.drawRightString(PAGE_WIDTH - MARGIN_RIGHT, PAGE_HEIGHT - 2 * cm,
                      "<Allegato I di cui all'articolo 7")

    y = PAGE_HEIGHT - 3.0 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(PAGE_WIDTH / 2, y,
                        "DICHIARAZIONE DI CONFORMITA' DELL'IMPIANTO ALLA REGOLA D'ARTE")
    y -= 14
    c.setFont("Helvetica", 10)
    c.drawCentredString(PAGE_WIDTH / 2, y, "Art.7, comma 1 del D.M. 22.1.2008 n.37")
    y -= 22

    # ── Dati fissi impresa ───────────────────────────────────────────────────
    y = para(c,
        "Il sottoscritto <b>Davide Mario Beccalossi</b> titolare dell'impresa "
        "<b>ITB Impianti Idraulici di Beccalossi Davide Mario</b> operante nel settore "
        "<b>impianti idraulici</b> con sede in <b>via Della Rocchetta, 26</b> a "
        "<b>Brescia</b>, telefono <b>3480650844</b> con partita Iva <b>02269030983</b>.",
        MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= 8

    y = para(c,
        "Iscritta nel registro delle imprese (d.P.R. 7/12/1995, n.581) della camera "
        "C.I.A.A. di <b>Brescia</b> n. <b>BCCDDM79M14B157C</b>;",
        MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= 4

    y = para(c,
        "Iscritta all'albo provinciale delle imprese artigiane (legge 8/8/1985, n.443) "
        "di <b>Brescia</b> n. <b>140291</b> esecutrice di un",
        MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= 2

    # Campo tipo impianto
    textfield(c, "tipo_impianto", MARGIN_LEFT, y - 14, CONTENT_WIDTH,
              tooltip="Es. nuovo impianto idraulico")
    y -= 24

    c.setFont("Helvetica", 10)
    c.drawString(MARGIN_LEFT, y, "Inteso come:")
    y -= 14
    textfield(c, "descrizione_impianto", MARGIN_LEFT, y, CONTENT_WIDTH,
              height=28, tooltip="Descrizione dettagliata dell'impianto")
    y -= 36

    # ── Dati variabili cliente / installazione ───────────────────────────────
    c.setFont("Helvetica", 10)
    lbl = "Commissionato da:"
    c.drawString(MARGIN_LEFT, y, lbl)
    lw = c.stringWidth(lbl, "Helvetica", 10)
    textfield(c, "commissionato_da", MARGIN_LEFT + lw + 4, y - 3,
              CONTENT_WIDTH - lw - 4, tooltip="Ragione sociale del cliente")
    y -= 18

    lbl = "installato nei locali siti nel comune di"
    c.drawString(MARGIN_LEFT, y, lbl)
    lw = c.stringWidth(lbl, "Helvetica", 10)
    textfield(c, "comune_installazione", MARGIN_LEFT + lw + 4, y - 3,
              CONTENT_WIDTH - lw - 4, tooltip="Comune di installazione")
    y -= 18

    lbl = "in via"
    c.drawString(MARGIN_LEFT, y, lbl)
    lw = c.stringWidth(lbl, "Helvetica", 10)
    textfield(c, "via_installazione", MARGIN_LEFT + lw + 4, y - 3,
              CONTENT_WIDTH - lw - 4, tooltip="Via di installazione")
    y -= 18

    lbl = "di proprietà Sig."
    c.drawString(MARGIN_LEFT, y, lbl)
    lw = c.stringWidth(lbl, "Helvetica", 10)
    textfield(c, "proprietario", MARGIN_LEFT + lw + 4, y - 3,
              CONTENT_WIDTH - lw - 4, tooltip="Proprietario immobile")
    y -= 22

    lbl = "In edificio adibito ad uso:"
    c.drawString(MARGIN_LEFT, y, lbl)
    lw = c.stringWidth(lbl, "Helvetica", 10)
    textfield(c, "uso_edificio", MARGIN_LEFT + lw + 4, y - 3,
              180, tooltip="Es. civile, commerciale")
    y -= 24

    # ── DICHIARA ─────────────────────────────────────────────────────────────
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(PAGE_WIDTH / 2, y, "DICHIARA")
    y -= 16

    y = para(c,
        "Sotto la propria personale responsabilità, che l'impianto è stato realizzato "
        "in modo conforme alla regola d'arte, secondo quanto previsto dall'art.6, tenuto "
        "conto delle condizioni di esercizio e degli usi a cui è destinato l'edificio "
        "avendo in particolare:",
        MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= 6

    # 3 checkbox DICHIARA (decide l'utente — default unchecked)
    dichiara_items = [
        ("dichiara_norma",
         "seguito la norma tecnica applicabile all'impiego UNI7129/2015;"),
        ("dichiara_componenti",
         "installato componenti e materiali adatti al luogo di installazione (art. 5 e 6);"),
        ("dichiara_controllo",
         "controllato l'impianto ai fini della sicurezza e della funzionalità con esito "
         "positivo, avendo eseguito le verifiche richieste dalle norme e dalle disposizioni "
         "di legge."),
    ]
    c.setFont("Helvetica", 10)
    for name, label in dichiara_items:
        checkbox(c, name, MARGIN_LEFT, y - 2, checked=False, tooltip=label)
        y = para(c, label, MARGIN_LEFT + 16, y, CONTENT_WIDTH - 16)
        y -= 2

    y -= 8

    # ── Allegati obbligatori (6 checkbox, tutti pre-checked) ─────────────────
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN_LEFT, y, "Allegati obbligatori:")
    y -= 14

    allegati_items = [
        ("allegato_progetto",
         "progetto ai sensi degli articoli 5 e 7"),
        ("allegato_relazione",
         "relazione con tipologie dei materiali utilizzati"),
        ("allegato_schema",
         "schema di impianto realizzato"),
        ("allegato_precedenti",
         "riferimento a dichiarazione di conformità precedenti o parziali, già esistenti"),
        ("allegato_certificato",
         "copia del certificato di riconoscimento dei requisiti tecnico-professionali"),
        ("allegato_conformita",
         "attestazione di conformità per impianto realizzato con materiali o sistemi "
         "non normalizzati"),
    ]
    c.setFont("Helvetica", 10)
    for name, label in allegati_items:
        checkbox(c, name, MARGIN_LEFT, y - 2, checked=True, tooltip=label)
        c.drawString(MARGIN_LEFT + 16, y, label[:90])  # single line each
        y -= 14

    y -= 8

    # ── DECLINA ──────────────────────────────────────────────────────────────
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(PAGE_WIDTH / 2, y, "DECLINA")
    y -= 16

    y = para(c,
        "Ogni responsabilità per sinistri a persone o a cose derivanti da manomissioni "
        "dell'impianto da parte di terzi ovvero da carenze di manutenzione o riparazione.",
        MARGIN_LEFT, y, CONTENT_WIDTH)
    y -= 28

    # ── Data e firme ─────────────────────────────────────────────────────────
    c.setFont("Helvetica", 10)
    c.drawString(MARGIN_LEFT, y, "Data")
    textfield(c, "data", MARGIN_LEFT + 30, y - 3, 90, tooltip="gg/mm/aaaa")
    c.drawString(MARGIN_LEFT + 150, y, "Il responsabile tecnico")
    c.drawString(MARGIN_LEFT + 330, y, "Il dichiarante")
    y -= 14
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN_LEFT + 150, y, "ITB Impianti Idraulici")
    c.drawString(MARGIN_LEFT + 330, y, "ITB Impianti Idraulici")

    c.showPage()
    c.save()
    print(f"Template PDF generato: {output}")


if __name__ == "__main__":
    build(OUTPUT_PATH)
