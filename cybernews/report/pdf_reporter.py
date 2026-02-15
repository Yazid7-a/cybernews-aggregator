from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def markdown_to_pdf(md_text: str, out_path: Path) -> None:
    """
    Render muy simple: imprime el markdown como texto monoespaciado.
    (Suficiente para un MVP; si quieres “PDF bonito”, lo siguiente es
    parsear headings/bold y maquetar mejor.)
    """
    out_path = Path(out_path)
    c = canvas.Canvas(str(out_path), pagesize=A4)
    width, height = A4

    # Fuente legible
    c.setFont("Courier", 9)

    left = 40
    top = height - 40
    y = top
    line_h = 12

    for raw_line in md_text.splitlines():
        line = raw_line.rstrip("\n")

        # salto de página
        if y < 40:
            c.showPage()
            c.setFont("Courier", 9)
            y = top

        # recorte suave si una línea es demasiado larga
        if len(line) > 140:
            line = line[:140] + "…"

        c.drawString(left, y, line)
        y -= line_h

    c.save()
