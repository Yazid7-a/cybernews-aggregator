from __future__ import annotations

from pathlib import Path
import typer

from cybernews.config import load_config
from cybernews.db import init_db, get_session
from cybernews.logging_conf import setup_logging

from cybernews.ingest.rss_ingestor import ingest_rss_sources
from cybernews.ingest.html_ingestor import ingest_html_sources

from cybernews.summarize.extractive import ExtractiveSummarizer
from cybernews.enrich.classifier import enrich_articles_batch

from cybernews.report.reporter import generate_report


app = typer.Typer(add_completion=False, help="CyberNews Aggregator (RSS/HTML) + reporte diario SOC-ready")


@app.command()
def main():
    """Comando placeholder (Typer muestra también este comando en --help)."""
    typer.echo("Usa: python main.py run --help")


@app.command()
def run(
    since: str = typer.Option("24h", help="Ventana temporal: ej '24h', '7d', '48h'."),
    output: Path = typer.Option(Path("reports"), help="Directorio de salida"),
    db_path: Path = typer.Option(Path("data/cybernews.sqlite"), help="Ruta SQLite"),
    pdf: bool = typer.Option(False, "--pdf/--no-pdf", help="Genera también report.pdf"),
    limit: int = typer.Option(25, "--limit", min=1, max=200, help="Máximo de noticias en el reporte"),
    log_level: str = typer.Option("INFO", "--log-level", help="DEBUG/INFO/WARNING/ERROR"),
):
    setup_logging(log_level)

    output.mkdir(parents=True, exist_ok=True)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    cfg = load_config(db_path=db_path, since=since, output_dir=output, pdf=pdf)
    engine = init_db(cfg.db_url)

    with get_session(engine) as session:
        rss_inserted = ingest_rss_sources(session, cfg)
        html_inserted = ingest_html_sources(session, cfg)

        summarizer = ExtractiveSummarizer(max_lines=5)
        enriched_count = enrich_articles_batch(session, cfg, summarizer)

        generated_paths = generate_report(
            session=session,
            cfg=cfg,
            since=since,
            output_dir=output,
            make_pdf=pdf,
            limit=limit,
        )

    typer.echo(f"RSS ingestados: {rss_inserted} | HTML ingestados: {html_inserted}")
    typer.echo(f"Artículos enriquecidos/resumidos (ventana): {enriched_count}")
    for p in generated_paths:
        typer.echo(f"Generado: {p}")


if __name__ == "__main__":
    app()
