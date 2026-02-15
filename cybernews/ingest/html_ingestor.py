from __future__ import annotations

import logging
from bs4 import BeautifulSoup

from cybernews.config import AppConfig
from cybernews.fetch.http_client import HttpClient
from cybernews.fetch.robots import RobotsCache
from cybernews.fetch.rate_limiter import DomainRateLimiter
from cybernews.models import Article
from cybernews.utils.urlnorm import canonicalize_url, get_domain, dedupe_hash
from cybernews.utils.text import clean_whitespace

log = logging.getLogger("ingest.html")

def ingest_html_sources(session, cfg: AppConfig) -> int:
    if not cfg.html_sources:
        return 0

    http = HttpClient(cfg.user_agent, cfg.timeout_s)
    robots = RobotsCache(http)
    limiter = DomainRateLimiter(cfg.per_domain_rps)

    inserted = 0
    for src in cfg.html_sources:
        name = src["name"]
        url = src["url"]
        selector = src.get("link_selector", "a")

        try:
            limiter.wait(url)
            if not robots.allowed(url, cfg.user_agent):
                log.warning("Robots bloquea HTML: %s (%s)", name, url)
                continue

            r = http.get(url)
            soup = BeautifulSoup(r.text, "html.parser")
            links = soup.select(selector)

            for a in links:
                href = a.get("href") or ""
                title = clean_whitespace(a.get_text(" ", strip=True) or "")
                if not href or not title:
                    continue
                if href.startswith("/"):
                    # relativo
                    base = url.rstrip("/")
                    href = base + href
                if not href.startswith("http"):
                    continue

                norm_url = canonicalize_url(href)
                domain = get_domain(norm_url)
                dkey = dedupe_hash(title, domain, None)

                exists = session.query(Article).filter(Article.url == norm_url).first()
                if exists:
                    continue

                art = Article(
                    source=name,
                    domain=domain,
                    title=title[:400],
                    url=norm_url,
                    canonical_url=None,
                    published_at=None,
                    content=None,
                    summary=None,
                    category=None,
                    severity=None,
                    soc_action=None,
                    dedupe_key=dkey,
                )
                session.add(art)
                inserted += 1

            log.info("HTML OK: %s | inserted=%d", name, inserted)

        except Exception as e:
            log.error("HTML FAIL: %s (%s) | %s", name, url, e)

    return inserted
