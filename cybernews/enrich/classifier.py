from __future__ import annotations

import logging
from datetime import datetime, timedelta

from cybernews.config import AppConfig
from cybernews.models import Article
from cybernews.enrich.severity import estimate_severity

log = logging.getLogger("enrich")

CATEGORY_RULES: list[tuple[str, list[str]]] = [
    ("ransomware", ["ransomware", "encrypt", "extortion", "locker"]),
    ("vulnerabilidades", ["cve-", "vulnerability", "zero-day", "0-day", "patch", "rce", "xss", "sqli", "csrf"]),
    ("apt", ["apt", "state-sponsored", "nation-state", "espionage"]),
    ("leaks/breaches", ["breach", "leak", "data stolen", "exposed", "compromised", "stolen data"]),
    ("cloud", ["aws", "azure", "gcp", "kubernetes", "docker", "cloud", "iam", "s3", "blob"]),
    ("phishing", ["phishing", "vishing", "smishing", "credential harvesting"]),
    ("malware", ["malware", "trojan", "botnet", "loader", "backdoor", "rat"]),
    ("ics/ot", ["ics", "scada", "ot", "plc"]),
]

SOC_ACTIONS: dict[str, str] = {
    "ransomware": "Revisar EDR por comportamiento de cifrado, verificar backups/restore, buscar notas/extorsión, y cazar IoCs (hashes, dominios, IPs).",
    "vulnerabilidades": "Priorizar patch/mitigación, revisar exposición (inventario/scan), buscar intentos de exploit en WAF/IDS y logs de autenticación.",
    "apt": "Hunting orientado a TTPs (MITRE), revisar endpoints críticos, credenciales, persistencia, y tráfico C2; activar detecciones temporales.",
    "leaks/breaches": "Validar alcance, revisar accesos anómalos, rotar credenciales/tokens, revisar logs de exfil y notificación interna.",
    "cloud": "Auditar IAM, accesos públicos, cambios de policy, claves/tokens, y logs (CloudTrail/AzureActivity); aplicar hardening rápido.",
    "phishing": "Buscar campañas en gateway/email, bloquear dominios/URLs, revisar endpoints que hicieron click, forzar reset MFA si aplica.",
    "malware": "Aislar host si hay indicios, extraer IoCs, revisar persistencia (run keys, services), y desplegar reglas YARA/EDR.",
    "ics/ot": "Revisar segmentación, accesos remotos/VPN, cambios en controladores, y alertas de integridad; coordinar con OT.",
}

def categorize(title: str) -> str:
    t = (title or "").lower()
    for cat, kws in CATEGORY_RULES:
        if any(k in t for k in kws):
            return cat
    return "general"

def soc_action_for(category: str, severity: str) -> str:
    base = SOC_ACTIONS.get(category, "Revisar logs/telemetría relevante, extraer IoCs, validar exposición y aplicar mitigaciones.")
    if severity == "alta":
        return base + " (ALTA) Elevar prioridad, abrir investigación y activar monitorización reforzada."
    if severity == "media":
        return base + " (MEDIA) Revisar en el día y ajustar detecciones."
    return base + " (BAJA) Monitorizar y registrar."

def enrich_articles_batch(session, cfg: AppConfig, summarizer) -> int:
    since_dt = datetime.utcnow() - timedelta(hours=cfg.since_hours)

    q = session.query(Article).filter(
        (Article.published_at == None) | (Article.published_at >= since_dt)  # noqa: E711
    )

    rows = q.all()
    updated = 0

    for art in rows:
        try:
            text_for_scoring = f"{art.title}\n{art.content or ''}"
            category = categorize(art.title)
            severity = estimate_severity(text_for_scoring)
            action = soc_action_for(category, severity)

            if not art.summary:
                art.summary = summarizer.summarize(art.content or art.title)

            art.category = category
            art.severity = severity
            art.soc_action = action
            updated += 1
        except Exception as e:
            log.error("Enrich fail (%s): %s", art.url, e)

    log.info("Enriched: %d", updated)
    return updated
