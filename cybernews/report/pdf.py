from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)

from cybernews.models import Article
from cybernews.utils.text import html_to_text, clamp_lines, clean_whitespace


@dataclass(frozen=True)
class PdfMeta:
    report_date: str
    since: str
    limit: int
    total: int


def _sev_color(sev: str | None) -> colors.Color:
    s = (sev or "").lower()
    if s in {"critica", "crítica"}:
        return colors.HexColor("#7B1FA2")
    if s == "alta":
        return colors.HexColor("#C62828")
    if s == "media":
        return colors.HexColor("#EF6C00")
    return colors.HexColor("#2E7D32")


def _sev_bg(sev: str | None) -> colors.Color:
    s = (sev or "").lower()
    if s in {"critica", "crítica"}:
        return colors.HexColor("#F3E5F5")
    if s == "alta":
        return colors.HexColor("#FFEBEE")
    if s == "media":
        return colors.HexColor("#FFF3E0")
    return colors.HexColor("#E8F5E9")


def _count_by_sev(articles: List[Article]) -> tuple[int, int, int, int]:
    crit = sum(1 for a in articles if (a.severity or "").lower() in {"critica", "crítica"})
    high = sum(1 for a in articles if (a.severity or "").lower() == "alta")
    med = sum(1 for a in articles if (a.severity or "").lower() == "media")
    low = sum(1 for a in articles if (a.severity or "").lower() == "baja" or not a.severity)
    return crit, high, med, low


def build_pdf_report(
    pdf_path: Path,
    meta: PdfMeta,
    articles: List[Article],
    top5: List[Article],
    trends: List[Tuple[str, int]],
) -> None:
    pdf_path = Path(pdf_path)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=1.6 * cm,
        rightMargin=1.6 * cm,
        topMargin=1.6 * cm,
        bottomMargin=1.6 * cm,
        title="Informe diario de ciberseguridad",
    )

    styles = getSampleStyleSheet()

    h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=18, spaceAfter=10)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=13, spaceBefore=10, spaceAfter=6)
    h3 = ParagraphStyle("h3", parent=styles["Heading3"], fontSize=11, spaceBefore=6, spaceAfter=4)

    normal = ParagraphStyle("normal", parent=styles["BodyText"], fontSize=10, leading=13)
    small = ParagraphStyle("small", parent=styles["BodyText"], fontSize=9, leading=12, textColor=colors.grey)

    # ✅ Estilos para celdas de tabla (WRAP real)
    th = ParagraphStyle(
        "th",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=11,
        textColor=colors.white,
        alignment=1,  # center
    )
    td = ParagraphStyle(
        "td",
        parent=styles["BodyText"],
        fontSize=9.3,
        leading=11,
        wordWrap="CJK",  # wrap más agresivo / fiable
    )
    td_center = ParagraphStyle(
        "td_center",
        parent=td,
        alignment=1,  # center
    )

    story = []

    # Header
    story.append(Paragraph(f"Informe diario de ciberseguridad — {meta.report_date}", h1))
    story.append(
        Paragraph(
            f"<b>Ventana:</b> últimas <b>{meta.since}</b>  &nbsp;&nbsp;|&nbsp;&nbsp;  "
            f"<b>Noticias:</b> {meta.total} (limit={meta.limit})",
            normal,
        )
    )
    story.append(Spacer(1, 8))

    crit, high, med, low = _count_by_sev(articles)

    # Executive summary
    summary_table = Table(
        [["Crítica", str(crit), "Alta", str(high), "Media", str(med), "Baja", str(low)]],
        colWidths=[2.2 * cm, 1.0 * cm, 2.0 * cm, 1.0 * cm, 2.0 * cm, 1.0 * cm, 2.0 * cm, 1.0 * cm],
    )
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (1, 0), _sev_bg("crítica")),
                ("BACKGROUND", (2, 0), (3, 0), _sev_bg("alta")),
                ("BACKGROUND", (4, 0), (5, 0), _sev_bg("media")),
                ("BACKGROUND", (6, 0), (7, 0), _sev_bg("baja")),
                ("TEXTCOLOR", (0, 0), (0, 0), _sev_color("crítica")),
                ("TEXTCOLOR", (2, 0), (2, 0), _sev_color("alta")),
                ("TEXTCOLOR", (4, 0), (4, 0), _sev_color("media")),
                ("TEXTCOLOR", (6, 0), (6, 0), _sev_color("baja")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (1, 0), (-1, 0), "CENTER"),
                ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
                ("GRID", (0, 0), (-1, 0), 0.25, colors.lightgrey),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("TOPPADDING", (0, 0), (-1, 0), 6),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ]
        )
    )
    story.append(summary_table)
    story.append(Spacer(1, 12))

    # Top 5
    story.append(Paragraph("Top 5 del día", h2))

    # ✅ Columnas ajustadas a ancho útil A4 con márgenes:
    # A4 ancho ≈ 21cm; márgenes 1.6+1.6 => útil ≈ 17.8cm
    # dejamos: # 0.9cm, titular 11.7cm, severidad 2.2cm, categoría 3.0cm => 17.8cm
    col_widths = [0.9 * cm, 11.7 * cm, 2.2 * cm, 3.0 * cm]

    table_data = [
        [
            Paragraph("#", th),
            Paragraph("Titular", th),
            Paragraph("Severidad", th),
            Paragraph("Categoría", th),
        ]
    ]

    for i, a in enumerate(top5, 1):
        title = html_to_text(a.title or "")
        sev = (a.severity or "baja").strip()
        cat = (a.category or "general").strip()

        table_data.append(
            [
                Paragraph(str(i), td_center),
                Paragraph(clean_whitespace(title), td),          # ✅ WRAP
                Paragraph(clean_whitespace(sev), td_center),     # ✅ centrado
                Paragraph(clean_whitespace(cat), td_center),     # ✅ centrado
            ]
        )

    top_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    top_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#263238")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor("#FAFAFA")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    # ✅ Colorear severidad (columna 2)
    for row in range(1, len(table_data)):
        sev_txt = top5[row - 1].severity or "baja"
        top_table.setStyle(
            TableStyle(
                [
                    ("TEXTCOLOR", (2, row), (2, row), _sev_color(sev_txt)),
                    ("FONTNAME", (2, row), (2, row), "Helvetica-Bold"),
                ]
            )
        )

    story.append(top_table)
    story.append(Spacer(1, 12))

    # Trends
    story.append(Paragraph("Tendencias", h2))
    if trends:
        trends_line = "  ".join([f"<b>{clean_whitespace(k)}</b> ({v})" for k, v in trends[:10]])
        story.append(Paragraph(trends_line, normal))
    else:
        story.append(Paragraph("Sin tendencias claras.", normal))

    story.append(PageBreak())

    # Detail
    story.append(Paragraph("Detalle por noticia", h2))
    story.append(Spacer(1, 4))

    for a in articles:
        title = html_to_text(a.title or "")
        sev = (a.severity or "baja")
        cat = (a.category or "general")
        pub = a.published_at.isoformat() if a.published_at else "n/d"

        summary = clamp_lines(html_to_text(a.summary or a.content or ""), max_lines=5)
        action = clamp_lines(html_to_text(a.soc_action or ""), max_lines=4)

        header = Table([[Paragraph(f"<b>{title}</b>", h3)]], colWidths=[17.8 * cm])
        header.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), _sev_bg(sev)),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        meta_line = Paragraph(
            f"<font color='grey'>Fuente:</font> {a.source} &nbsp; | &nbsp; "
            f"<font color='grey'>Publicado:</font> {pub} &nbsp; | &nbsp; "
            f"<font color='grey'>Categoría:</font> <b>{cat}</b> &nbsp; | &nbsp; "
            f"<font color='grey'>Severidad:</font> <font color='{_sev_color(sev).hexval()}'><b>{sev}</b></font>",
            small,
        )
        url_line = Paragraph(f"<font color='grey'>URL:</font> {a.url}", small)

        body = [
            header,
            Spacer(1, 6),
            meta_line,
            url_line,
            Spacer(1, 8),
            Paragraph("<b>Resumen (3–5 líneas):</b>", normal),
            Paragraph(summary or "(sin resumen)", normal),
            Spacer(1, 8),
            Paragraph("<b>Qué debería mirar un SOC:</b>", normal),
            Paragraph(action or "(sin recomendación)", normal),
            Spacer(1, 14),
        ]

        story.append(KeepTogether(body))

    doc.build(story)
