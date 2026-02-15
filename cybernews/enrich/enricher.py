import logging
from dataclasses import dataclass
from typing import Optional

from cybernews.utils.text import html_to_text, clamp_lines

log = logging.getLogger("enrich")


@dataclass
class EnrichedArticle:
    title: str
    url: str
    source: str
    domain: str
    published_at: Optional[str]  # ya formateado
    category: str
    severity: str
    summary: str
    soc_reco: str


CATEGORY_KEYWORDS = {
    "ransomware": ["ransomware", "lockbit", "encrypt", "extortion", "double extortion"],
    "vulnerabilidades": ["cve-", "zero-day", "0day", "rce", "sql injection", "xss", "patch", "cvss"],
    "apt": ["apt", "nation-state", "espionage", "intrusion set", "campaign"],
    "leaks/breaches": ["breach", "leak", "exposed", "data theft", "records", "stolen data"],
    "cloud": ["aws", "azure", "gcp", "kubernetes", "docker", "iam", "cloudtrail", "tenant"],
    "malware": ["stealer", "trojan", "botnet", "rat", "loader", "worm"],
}

SEVERITY_KEYWORDS = {
    "alta": ["critical", "actively exploited", "kev", "zero-day", "pre-auth rce", "rce", "cvss 9", "cvss 10"],
    "media": ["high", "exploited", "patch", "malware", "phishing", "botnet"],
    "baja": ["update", "guide", "report", "analysis", "research", "insights"],
}


def classify_category(text: str) -> str:
    t = text.lower()
    for cat, kws in CATEGORY_KEYWORDS.items():
        if any(k in t for k in kws):
            return cat
    return "general"


def estimate_severity(text: str) -> str:
    t = text.lower()
    for sev in ("alta", "media", "baja"):
        if any(k in t for k in SEVERITY_KEYWORDS[sev]):
            return sev
    return "baja"


def soc_recommendation(category: str, severity: str) -> str:
    if category == "vulnerabilidades":
        return "Priorizar patch/mitigación, revisar exposición (inventario/scan), y buscar intentos de exploit en logs/WAF/IDS."
    if category == "ransomware":
        return "Revisar EDR por comportamiento de cifrado, verificar backups/restore, y cazar IoCs (hashes, dominios, IPs)."
    if category == "apt":
        return "Hunting por TTPs (MITRE), revisar endpoints críticos, persistencia y tráfico C2; elevar monitorización temporal."
    if category == "leaks/breaches":
        return "Validar alcance, revisar accesos anómalos, rotar credenciales/tokens y buscar indicios de exfiltración."
    if category == "cloud":
        return "Auditar IAM, accesos públicos, cambios de policy y logs (CloudTrail/AzureActivity); aplicar hardening rápido."
    if category == "malware":
        return "Aislar host si hay indicios, extraer IoCs, revisar persistencia (run keys/services) y desplegar reglas YARA/EDR."
    return "Revisar telemetría, extraer IoCs si existen, validar exposición y aplicar mitigaciones razonables."


def enrich_article(
    title: str,
    url: str,
    source: str,
    domain: str,
    published_at_str: Optional[str],
    raw_text: str,
    summarizer,
) -> EnrichedArticle:
    clean = html_to_text(raw_text)
    # Resumen extractivo/LLM (lo que tengas), pero SIEMPRE lo limpiamos y lo acotamos
    summary_raw = summarizer.summarize(clean, max_sentences=5) if summarizer else clean
    summary_clean = clamp_lines(html_to_text(summary_raw), max_lines=5)

    category = classify_category(f"{title} {summary_clean}")
    severity = estimate_severity(f"{title} {summary_clean}")

    return EnrichedArticle(
        title=title,
        url=url,
        source=source,
        domain=domain,
        published_at=published_at_str,
        category=category,
        severity=severity,
        summary=summary_clean,
        soc_reco=soc_recommendation(category, severity),
    )
