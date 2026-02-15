from __future__ import annotations

import hashlib
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "gclid", "fbclid", "mc_cid", "mc_eid",
}

def get_domain(url: str) -> str:
    p = urlparse(url)
    return (p.netloc or "").lower()

def canonicalize_url(url: str) -> str:
    """
    Normaliza: lower host, quita fragment, ordena query y elimina tracking params comunes.
    """
    p = urlparse(url)
    query = [(k, v) for (k, v) in parse_qsl(p.query, keep_blank_values=True) if k not in TRACKING_PARAMS]
    query.sort()
    new_p = p._replace(
        scheme=p.scheme.lower() if p.scheme else "https",
        netloc=p.netloc.lower(),
        fragment="",
        query=urlencode(query, doseq=True),
    )
    return urlunparse(new_p)

def dedupe_hash(title: str, domain: str, date_iso: str | None) -> str:
    base = f"{title.strip().lower()}|{domain.strip().lower()}|{date_iso or ''}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()
