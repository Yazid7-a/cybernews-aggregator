from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from cybernews.sources import RSS_SOURCES, HTML_SOURCES
from cybernews.utils.timeparse import parse_since_to_hours

@dataclass(frozen=True)
class AppConfig:
    db_url: str
    since_hours: int
    output_dir: Path
    make_pdf: bool
    user_agent: str
    timeout_s: int
    per_domain_rps: float
    rss_sources: list[dict]
    html_sources: list[dict]

def load_config(db_path: Path, since: str, output_dir: Path, pdf: bool) -> AppConfig:
    hours = parse_since_to_hours(since)
    return AppConfig(
        db_url=f"sqlite:///{db_path.as_posix()}",
        since_hours=hours,
        output_dir=output_dir,
        make_pdf=pdf,
        user_agent="CyberNewsAggregator/0.1 (+portfolio; respectful scraping)",
        timeout_s=15,
        per_domain_rps=0.5,  # 0.5 req/s => 1 req cada 2s por dominio
        rss_sources=RSS_SOURCES,
        html_sources=HTML_SOURCES,
    )
