from __future__ import annotations

KEYWORDS_HIGH = [
    "zero-day", "0-day", "rce", "remote code execution", "worm", "critical", "actively exploited",
    "exploited in the wild", "cve-", "unauthenticated", "privilege escalation", "supply chain",
    "ransomware", "data leak", "breach", "mass exploitation",
]
KEYWORDS_MED = [
    "vulnerability", "patch", "phishing", "malware", "botnet", "ddos", "credential", "token",
    "backdoor", "loader", "exploit", "poc",
]

def estimate_severity(text: str) -> str:
    t = (text or "").lower()
    score = 0
    for k in KEYWORDS_HIGH:
        if k in t:
            score += 3
    for k in KEYWORDS_MED:
        if k in t:
            score += 1

    if score >= 5:
        return "alta"
    if score >= 2:
        return "media"
    return "baja"
