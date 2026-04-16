#!/usr/bin/env python3
"""
Genera il template PDF della Dichiarazione di Conformità con campi AcroForm
compilabili. Mantiene fissi i dati di ITB Impianti Idraulici (Davide Beccalossi)
e rende variabili i dati del cliente, luogo di installazione, ecc.

Uso:
    python scripts/build_template.py

Il PDF viene salvato in pdf_templates/dichiarazione_conformita.pdf
"""
from pathlib import Path

from reportlab.lib.colors import black, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

PAGE_WIDTH, PAGE_HEIGHT = A4  # 595 x 842 pt
MARGIN_LEFT = 2 * cm
MARGIN_RIGHT = 2 * cm
CONTENT_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "pdf_templates" / "dichiarazione_conformita.pdf"


def draw_paragraph(c: canvas.Canvas, text: str, x: float, y: float, width: float,
                   font_name: str = "Helvetica", font_size: int = 9,
                   leading: float = 11, alignment: int = 0) -> float:
    """Disegna un paragrafo wrapped e ritorna la nuova Y (sotto il paragrafo)."""
    style = ParagraphStyle(
        name="p",
        fontName=font_name,
        fontSize=font_size,
        leading=leading,
        alignment=alignment,
        textColor=black,
    )
    p = Paragraph(text, style)
    w, h = p.wrap(width, 1000)
    p.drawOn(c, x, y - h)
    return y - h


def draw_field(c: canvas.Canvas, name: str, x: float, y: float,
               width: float, height: float = 14, tooltip: str = "",
               font_size: int = 9) -> None:
    """Aggiunge un campo AcroForm di testo al canvas."""
    c.acroForm.textfield(
        name=name,
        tooltip=tooltip or name,
        x=x,
        y=y,
        width=width,
        height=height,
        borderStyle="underlined",
        borderColor=black,
        fillColor=white,
        textColor=black,
        forceBorder=False,
        fontSize=font_size,
        fontName="Helvetica",
    )


def draw_checkbox(c: canvas.Canvas, name: str, x: float, y: float,
                  size: float = 10, checked: bool = False,
                  tooltip: str = "") -> None:
    """Aggiunge una checkbox AcroForm."""
    c.acroForm.checkbox(
        name=name,
        tooltip=tooltip or name,
        x=x,
        y=y,
        size=size,
        checked=checked,
        buttonStyle="check",
        borderColor=black,
        fillColor=white,
    )


def build_template(output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(output), pagesize=A4)
    c.setTitle("Dichiarazione di Conformita")

    # Header allegato (in alto a destra)
    c.setFont("Helvetica-Bold", 9)
    c.drawRightString(PAGE_WIDTH - MARGIN_RIGHT, PAGE_HEIGHT - 2 * cm,
                      "<Allegato I di cui all'articolo 7")

    # Titolo
    y = PAGE_HEIGHT - 3.0 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(PAGE_WIDTH / 2, y,
                        "DICHIARAZIONE DI CONFORMITA' DELL'IMPIANTO ALLA REGOLA D'ARTE")
    y -= 14
    c.setFont("Helvetica", 10)
    c.drawCentredString(PAGE_WIDTH / 2, y, "Art.7, comma 1 del D.M. 22.1.2008 n.37")
    y -= 20

    # Paragrafo introduttivo con dati fissi ITB
    intro = (
        "Il sottoscritto <b>Davide Mario Beccalossi</b> titolare dell'impresa "
        "<b>ITB Impianti Idraulici di Beccalossi Davide Mario</b> operante nel settore "
        "<b>impianti idraulici</b> con sede in <b>via Della Rocchetta, 26</b> a "
        "<b>Brescia</b>, telefono <b>3480650844</b> con partita Iva <b>02269030983</b>."
    )
    y = draw_paragraph(c, intro, MARGIN_LEFT, y, CONTENT_WIDTH, font_size=10, leading=13)
    y -= 8

    # Camera di commercio
    ccia = (
        "Iscritta nel registro delle imprese (d.P.R. 7/12/1995, n.581) della camera "
        "C.I.A.A. di <b>Brescia</b> n. <b>BCCDDM79M14B157C</b>;"
    )
    y = draw_paragraph(c, ccia, MARGIN_LEFT, y, CONTENT_WIDTH, font_size=10, leading=13)
    y -= 4

    albo = (
        "Iscritta all'albo provinciale delle imprese artigiane (legge 8/8/1985, n.443) "
        "di <b>Brescia</b> n. <b>140291</b> esecutrice di un"
    )
    y = draw_paragraph(c, albo, MARGIN_LEFT, y, CONTENT_WIDTH, font_size=10, leading=13)
    y -= 2

    # Campo: tipo impianto (es. "nuovo impianto idraulico")
    draw_field(c, "tipo_impianto", MARGIN_LEFT, y - 14,
               CONTENT_WIDTH, height=14, tooltip="Es. nuovo impianto idraulico")
    y -= 22

    # "Inteso come:" + campo
    c.setFont("Helvetica", 10)
    c.drawString(MARGIN_LEFT, y, "Inteso come:")
    y -= 14
    draw_field(c, "descrizione_impianto", MARGIN_LEFT, y, CONTENT_WIDTH, height=32,
               tooltip="Descrizione dettagliata dell'impianto realizzato")
    y -= 40

    # "Commissionato da:" + campo cliente
    c.setFont("Helvetica", 10)
    label = "Commissionato da:"
    c.drawString(MARGIN_LEFT, y, label)
    label_w = c.stringWidth(label, "Helvetica", 10)
    draw_field(c, "commissionato_da", MARGIN_LEFT + label_w + 4, y - 3,
               CONTENT_WIDTH - label_w - 4, height=14,
               tooltip="Ragione sociale del cliente")
    y -= 18

    # "installato nei locali siti nel comune di" + comune
    c.drawString(MARGIN_LEFT, y, "installato nei locali siti nel comune di")
    label_w = c.stringWidth("installato nei locali siti nel comune di", "Helvetica", 10)
    draw_field(c, "comune_installazione", MARGIN_LEFT + label_w + 4, y - 3,
               CONTENT_WIDTH - label_w - 4, height=14,
               tooltip="Comune dove è stato installato l'impianto")
    y -= 18

    # "in via" + via installazione
    c.drawString(MARGIN_LEFT, y, "in via")
    label_w = c.stringWidth("in via", "Helvetica", 10)
    draw_field(c, "via_installazione", MARGIN_LEFT + label_w + 4, y - 3,
               CONTENT_WIDTH - label_w - 4, height=14,
               tooltip="Indirizzo dove è stato installato l'impianto")
    y -= 18

    # "di proprietà Sig." + proprietario
    c.drawString(MARGIN_LEFT, y, "di proprietà Sig.")
    label_w = c.stringWidth("di proprietà Sig.", "Helvetica", 10)
    draw_field(c, "proprietario", MARGIN_LEFT + label_w + 4, y - 3,
               CONTENT_WIDTH - label_w - 4, height=14,
               tooltip="Nome del proprietario dell'immobile")
    y -= 22

    # "In edificio adibito ad uso:" + uso
    c.drawString(MARGIN_LEFT, y, "In edificio adibito ad uso:")
    label_w = c.stringWidth("In edificio adibito ad uso:", "Helvetica", 10)
    draw_field(c, "uso_edificio", MARGIN_LEFT + label_w + 4, y - 3,
               180, height=14,
               tooltip="Es. civile, commerciale, industriale")
    y -= 22

    # DICHIARA header
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(PAGE_WIDTH / 2, y, "DICHIARA")
    y -= 16

    # Paragrafo DICHIARA
    dichiara = (
        "Sotto la propria personale responsabilità, che l'impianto è stato realizzato "
        "in modo conforme alla regola d'arte, secondo quanto previsto dall'art.6, tenuto "
        "conto delle condizioni di esercizio e degli usi a cui è destinato l'edificio "
        "avendo in particolare:"
    )
    y = draw_paragraph(c, dichiara, MARGIN_LEFT, y, CONTENT_WIDTH, font_size=10, leading=13)
    y -= 4

    # Elenco puntato fisso (✓)
    bullets = [
        "seguito la norma tecnica applicabile all'impiego UNI7129/2015;",
        "installato componenti e materiali adatti al luogo di installazione (art. 5 e 6);",
        "controllato l'impianto ai fini della sicurezza e della funzionalità con esito "
        "positivo, avendo eseguito le verifiche richieste dalle norme e dalle disposizioni "
        "di legge.",
    ]
    c.setFont("Helvetica", 10)
    for b in bullets:
        c.drawString(MARGIN_LEFT + 4, y - 10, "\u2713")
        y = draw_paragraph(c, b, MARGIN_LEFT + 16, y, CONTENT_WIDTH - 16,
                           font_size=10, leading=13)
        y -= 2

    y -= 6

    # Allegati — sezione 1: opzionali (decide l'utente)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN_LEFT, y, "Allegati obbligatori:")
    y -= 14

    allegati_opzionali = [
        ("allegato_progetto", "progetto ai sensi degli articoli 5 e 7"),
        ("allegato_relazione", "relazione con tipologie dei materiali utilizzati"),
        ("allegato_schema", "schema di impianto realizzato"),
    ]
    c.setFont("Helvetica", 10)
    for name, label in allegati_opzionali:
        draw_checkbox(c, name, MARGIN_LEFT + 2, y - 2, size=10, checked=False, tooltip=label)
        c.drawString(MARGIN_LEFT + 18, y, label)
        y -= 14

    # Allegati — sezione 2: obbligatori (pre-checked)
    allegati_obbligatori = [
        ("allegato_precedenti", "riferimento a dichiarazione di conformità precedenti o parziali, già esistenti"),
        ("allegato_certificato", "copia del certificato di riconoscimento dei requisiti tecnico-professionali"),
        ("allegato_conformita", "attestazione di conformità per impianto realizzato con materiali o sistemi non normalizzati"),
    ]
    for name, label in allegati_obbligatori:
        draw_checkbox(c, name, MARGIN_LEFT + 2, y - 2, size=10, checked=True, tooltip=label)
        c.drawString(MARGIN_LEFT + 18, y, label)
        y -= 14

    y -= 8

    # DECLINA header
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(PAGE_WIDTH / 2, y, "DECLINA")
    y -= 16

    declina = (
        "Ogni responsabilità per sinistri a persone o a cose derivanti da manomissioni "
        "dell'impianto da parte di terzi ovvero da carenze di manutenzione o riparazione."
    )
    y = draw_paragraph(c, declina, MARGIN_LEFT, y, CONTENT_WIDTH, font_size=10, leading=13)
    y -= 28

    # Data + firme
    c.setFont("Helvetica", 10)
    c.drawString(MARGIN_LEFT, y, "Data")
    draw_field(c, "data", MARGIN_LEFT + 30, y - 3, 90, height=14, tooltip="gg/mm/aaaa")

    c.drawString(MARGIN_LEFT + 150, y, "Il responsabile tecnico")
    c.drawString(MARGIN_LEFT + 320, y, "Il dichiarante")
    y -= 14
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN_LEFT + 150, y, "ITB Impianti Idraulici")
    c.drawString(MARGIN_LEFT + 320, y, "ITB Impianti Idraulici")

    c.showPage()
    c.save()
    print(f"Template PDF generato: {output}")


if __name__ == "__main__":
    build_template(OUTPUT_PATH)
