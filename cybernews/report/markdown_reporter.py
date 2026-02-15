from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import List

from cybernews.models import Article
from cybernews.utils.text import clean_whitespace


def _top_terms(titles: List[str], n: int = 10) -> List[tuple[str, int]]:
    words = []
    for t in titles:
        t = clean_whitespace(t).lower()
        words.extend([w.strip(".,:;()[]{}'\"!?") for w in t.split() if len(w) >= 4])

    # stopwords mínimas (ajusta a tu gusto)
    stop = {
        "with", "this", "that", "from", "have", "will", "their", "they", "into",
        "over", "more", "after", "than", "your", "what", "when", "been", "using",
        "says", "said", "report", "reports", "today",
    }
    words = [w for w in words if w and w not in stop]
    return Counter(words).most_common(n)


def build_markdown_report(articles: List[Article], since: str, limit: int) -> str:
    # Top 5 por severidad + reciente (fallback si falta severidad)
    def sev_rank(a: Article) -> int:
        m = {"critica": 4, "crítica": 4, "alta": 3, "media": 2, "baja": 1}
        s = (a.severity or "").strip().lower()
        return m.get(s, 0)

    top5 = sorted(articles, key=lambda a: (sev_rank(a), a.published_at or 0), reverse=True)[:5]

    titles = [a.title or "" for a in articles]
    trends = _top_terms(titles, n=10)
    trends_str = ", ".join([f"`{t}`({c})" for t, c in trends]) if trends else "(sin datos)"

    lines = []
    lines.append(f"# Informe diario de ciberseguridad — {__import__('datetime').date.today().isoformat()}")
    lines.append(f"Ventana analizada: últimas **{since}**")
    lines.append(f"Noticias incluidas en reporte: **{len(articles)}** (limit={limit})")
    lines.append("")
    lines.append("## Top 5 del día")
    for i, a in enumerate(top5, 1):
        sev = (a.severity or "n/a").lower()
        cat = a.category or "general"
        lines.append(f"{i}. **{a.title}** ")
        lines.append(f" - Severidad: **{sev}** | Categoría: **{cat}** ")
        lines.append(f" - URL: {a.url}")
    lines.append("")
    lines.append("## Tendencias (términos repetidos)")
    lines.append(trends_str)
    lines.append("")
    lines.append("## Detalle por noticia")

    for a in articles:
        sev = (a.severity or "baja").upper()
        cat = a.category or "general"
        pub = a.published_at.isoformat() if a.published_at else "n/a"

        lines.append(f"### {a.title}")
        lines.append(f"- Fuente: **{a.source}** | Dominio: `{a.domain}`")
        lines.append(f"- Publicado: **{pub}**")
        lines.append(f"- Categoría: **{cat}** | Severidad: **{(a.severity or 'baja')}**")
        lines.append(f"- URL: {a.url}")

        summary = a.summary or a.content or ""
        summary = clean_whitespace(summary)
        if summary:
            # “3–5 líneas” aproximado: limitamos tamaño
            summary = summary[:600]
            lines.append("**Resumen (3–5 líneas):**")
            lines.append(summary)
        else:
            lines.append("**Resumen (3–5 líneas):**")
            lines.append("(sin resumen disponible)")

        # Acción SOC simple (puedes hacerlo más inteligente con tu lógica de enrich)
        lines.append("**Qué debería mirar un SOC:**")
        if (a.severity or "").lower() in {"alta", "crítica", "critica"}:
            lines.append("Priorizar patch/mitigación, revisar exposición (inventario/scan), buscar intentos de exploit en WAF/IDS y logs de autenticación.")
            lines.append("(ALTA) Elevar prioridad, abrir investigación y activar monitorización reforzada.")
        elif (a.severity or "").lower() == "media":
            lines.append("Validar alcance, revisar actividad anómala, extraer IoCs y ajustar detecciones/alertas.")
            lines.append("(MEDIA) Revisar en el día y ajustar detecciones.")
        else:
            lines.append("Revisar logs/telemetría relevante, extraer IoCs, validar exposición y aplicar mitigaciones.")
            lines.append("(BAJA) Monitorizar y registrar.")

        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
