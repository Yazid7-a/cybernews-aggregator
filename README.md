\# CyberNews Aggregator — Daily SOC Report (MD/PDF)



A Python 3.11+ project that aggregates \*\*public cybersecurity news\*\* (RSS-first), normalizes \& deduplicates entries, enriches them (summary/category/severity/SOC action), and generates a daily \*\*SOC-ready report\*\* in \*\*Markdown\*\* and \*\*PDF\*\*.



> ✅ Ethical-by-design: public sources only, \*\*robots.txt respected\*\*, per-domain \*\*rate limiting\*\*, and per-source error handling (pipeline won’t crash on a single feed failure).



---



\## Preview



!\[PDF Top 5 Preview](assets/pdf\_top5.png)



(See more in `examples/`.)



---



\## Features



\### Ingestion (RSS/HTML)

\- RSS-first ingestion (preferred when available)

\- HTML ingestion (requests + BeautifulSoup) supported when needed

\- Robust error handling per source

\- Rate limiting per domain

\- robots.txt checks before fetching



\### Normalization \& Deduplication

\- URL normalization (canonicalization when possible)

\- Dedup key based on: \*\*title + domain + date\*\*

\- SQLite persistence for reliable incremental runs



\### Enrichment (SOC-focused)

For each article:

\- 3–5 line summary (extractive summarizer fallback)

\- Category (e.g., ransomware, vulnerabilities, APT, leaks, cloud…)

\- Estimated severity (low/medium/high)

\- “SOC action”: quick guidance on what to check (patching, IoCs, detections, logs)



\### Output

\- `report\_YYYY-MM-DD.md`

\- `report\_YYYY-MM-DD.pdf` (formatted for readability)



---



\## Quickstart



\### 1) Setup (Windows)

```powershell

python -m venv venv

.\\venv\\Scripts\\activate

pip install -r requirements.txt



2\) Run

python main.py run --since 24h --output .\\reports --pdf --limit 25





Parameters



--since 24h → time window (24h, 48h, 7d, etc.)



--output → output directory for reports



--pdf → also generate PDF



--limit → max articles in the report



Example Output



Sample reports are included:



examples/report\_sample.md



examples/report\_sample.pdf



Tech Stack



Python 3.11+



Typer (CLI)



Requests + BeautifulSoup



SQLAlchemy + SQLite



ReportLab (PDF)



Pytest (tests)



Project Structure (high level)



cybernews/ingest/ → RSS/HTML ingestors



cybernews/fetch/ → HTTP client, robots, rate limiting



cybernews/enrich/ → classification (category/severity/SOC action)



cybernews/summarize/ → extractive summarizer



cybernews/report/ → Markdown + PDF report generation



cybernews/db.py + cybernews/models.py → persistence



Notes on Legal \& Ethical Use



This project processes public content only and follows:



robots.txt checks



per-domain rate limiting



polite, non-intrusive fetching



Roadmap (Future Improvements)



Docker + docker-compose



GitHub Actions (CI: run tests on push)



Scheduler (cron / Windows Task Scheduler)



Optional LLM summarizer via a Summarizer interface (plug-in)



Author



Yazid (Yazid7-a)

Repo: https://github.com/Yazid7-a/cybernews-aggregator

