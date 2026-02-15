from __future__ import annotations

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple
from collections import Counter

from cybernews.config import AppConfig
from cybernews.models import Article
from cybernews.report.markdown_reporter import build_markdown_report
from cybernews.report.pdf import build_pdf_report, PdfMeta
from cybernews.utils.text import clean_whitespace

log = logging.getLogger("report")


def _select_articles_for_window(session, cfg: AppConfig, limit: int) -> List[Article]:
    since_dt = datetime.utcnow() - timedelta(hours=cfg.since_hours)

    # incluimos published_at None (algunos feeds no dan fecha), pero los empujamos al final
    rows = (
        session.query(Article)
        .filter((Article.published_at == None) | (Article.published_at >= since_dt))  # noqa: E711
        .order_by(Article.published_at.desc().nullslast(), Article.id.desc())
        .all()
    )

    return rows[:limit]


def _top_terms(titles: List[str], n: int = 10) -> List[Tuple[str, int]]:
    words = []
    stop = {
        "with", "this", "that", "from", "have", "will", "their", "they", "into",
        "over", "more", "after", "than", "your", "what", "when", "been", "using",
        "says", "said", "report", "reports", "today",
        "para", "como", "esta", "este", "sobre", "entre", "pero", "porque",
    }

    for t in titles:
        t = clean_whitespace(t).lower()
        for w in t.split():
            w = w.strip(".,:;()[]{}'\"!?")
            if len(w) < 4:
                continue
            if w in stop:
                continue
            words.append(w)

    return Counter(words).most_common(n)


def _severity_rank(sev: str | None) -> int:
    s = (sev or "").lower()
    if s in {"critica", "crítica"}:
        return 4
    if s == "alta":
        return 3
    if s == "media":
        return 2
    if s == "baja":
        return 1
    return 0


def generate_report(
    session,
    cfg: AppConfig,
    since: str,
    output_dir: Path,
    make_pdf: bool,
    limit: int,
) -> List[str]:
    output_dir.mkdir(parents=True, exist_ok=True)

    articles = _select_articles_for_window(session, cfg=cfg, limit=limit)

    # Top 5: severidad + recencia
    top5 = sorted(
        articles,
        key=lambda a: (_severity_rank(a.severity), a.published_at or datetime.min),
        reverse=True,
    )[:5]

    trends = _top_terms([a.title or "" for a in articles], n=10)

    # Markdown
    md_text = build_markdown_report(articles=articles, since=since, limit=limit)

    stamp = datetime.utcnow().strftime("%Y-%m-%d")
    md_path = output_dir / f"report_{stamp}.md"
    md_path.write_text(md_text, encoding="utf-8")

    generated = [str(md_path)]

    # PDF bonito
    if make_pdf:
        pdf_path = output_dir / f"report_{stamp}.pdf"
        meta = PdfMeta(
            report_date=stamp,
            since=since,
            limit=limit,
            total=len(articles),
        )
        build_pdf_report(
            pdf_path=pdf_path,
            meta=meta,
            articles=articles,
            top5=top5,
            trends=trends,
        )
        generated.append(str(pdf_path))

    log.info("Report generated: %s", generated)
    return generated
