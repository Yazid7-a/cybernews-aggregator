from __future__ import annotations

import logging
from datetime import datetime

import feedparser
from dateutil import parser as dtparser

from cybernews.config import AppConfig
from cybernews.fetch.http_client import HttpClient
from cybernews.fetch.robots import RobotsCache
from cybernews.fetch.rate_limiter import DomainRateLimiter
from cybernews.models import Article
from cybernews.utils.urlnorm import canonicalize_url, get_domain, dedupe_hash
from cybernews.utils.text import clean_whitespace, strip_html

log = logging.getLogger("ingest.rss")


def _parse_datetime(entry) -> datetime | None:
    """
    Intenta parsear fechas RSS/Atom de forma robusta:
    - entry.published / entry.updated (string)
    - entry.published_parsed / updated_parsed (time.struct_time)
    """
    published = getattr(entry, "published", None)
    if published:
        try:
            return dtparser.parse(published).replace(tzinfo=None)
        except Exception:
            pass

    updated = getattr(entry, "updated", None)
    if updated:
        try:
            return dtparser.parse(updated).replace(tzinfo=None)
        except Exception:
            pass

    published_parsed = getattr(entry, "published_parsed", None)
    if published_parsed:
        try:
            return datetime(*published_parsed[:6])
        except Exception:
            pass

    updated_parsed = getattr(entry, "updated_parsed", None)
    if updated_parsed:
        try:
            return datetime(*updated_parsed[:6])
        except Exception:
            pass

    return None


def _entry_content(entry) -> str:
    """
    Extrae contenido de forma razonable:
    - summary
    - content[0].value
    """
    if getattr(entry, "summary", None):
        return str(entry.summary)

    content = getattr(entry, "content", None)
    if content and isinstance(content, list) and len(content) > 0:
        val = getattr(content[0], "value", "")
        return str(val) if val else ""

    return ""


def ingest_rss_sources(session, cfg: AppConfig) -> int:
    http = HttpClient(cfg.user_agent, cfg.timeout_s)
    robots = RobotsCache(http)
    limiter = DomainRateLimiter(cfg.per_domain_rps)

    inserted_total = 0

    for src in cfg.rss_sources:
        name = src["name"]
        url = src["url"]

        try:
            limiter.wait(url)

            if not robots.allowed(url, cfg.user_agent):
                log.warning("Robots bloquea RSS: %s (%s)", name, url)
                continue

            r = http.get(url)
            feed = feedparser.parse(r.text)

            if getattr(feed, "bozo", 0):
                log.warning("RSS BOZO: %s | %s", name, getattr(feed, "bozo_exception", "unknown"))

            entries = getattr(feed, "entries", []) or []
            inserted_this_source = 0

            for e in entries:
                title = clean_whitespace(getattr(e, "title", "") or "")
                link = (getattr(e, "link", "") or "").strip()
                if not title or not link:
                    continue

                norm_url = canonicalize_url(link)
                domain = get_domain(norm_url)

                published = _parse_datetime(e)
                date_iso = published.date().isoformat() if published else None

                # Dedupe: URL (unique) + hash estable
                dkey = dedupe_hash(title, domain, date_iso)

                exists = session.query(Article).filter(Article.url == norm_url).first()
                if exists:
                    continue

                content = _entry_content(e)
                content = clean_whitespace(strip_html(content))
                if content:
                    content = content[:8000]

                art = Article(
                    source=name,
                    domain=domain,
                    title=title[:400],
                    url=norm_url,
                    canonical_url=None,
                    published_at=published,
                    content=content or None,
                    summary=None,
                    category=None,
                    severity=None,
                    soc_action=None,
                    dedupe_key=dkey,
                )

                session.add(art)
                inserted_total += 1
                inserted_this_source += 1

            log.info("RSS OK: %s | items=%d | inserted=%d", name, len(entries), inserted_this_source)

        except Exception as e:
            log.error("RSS FAIL: %s (%s) | %s", name, url, e)

    return inserted_total
