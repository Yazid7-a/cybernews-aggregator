import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

import requests
import xml.etree.ElementTree as ET

from cybernews.utils.text import html_to_text

log = logging.getLogger("ingest.rss")


@dataclass
class RssItem:
    title: str
    url: str
    source: str
    published_at: Optional[datetime]
    summary_raw: str


def _safe_dt(dt_str: str) -> Optional[datetime]:
    """
    Intento básico de parseo de fechas comunes RSS/Atom sin dependencias extra.
    (Si ya usas dateutil en tu proyecto, mejor parsear con dateutil.parser.)
    """
    if not dt_str:
        return None
    try:
        # Intento ISO
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        return None


def fetch_rss(url: str, timeout: int = 20) -> str:
    r = requests.get(url, timeout=timeout, headers={"User-Agent": "CyberNewsAggregator/1.0"})
    r.raise_for_status()
    return r.text


def parse_rss(feed_xml: str, source_name: str) -> list[RssItem]:
    """
    Parser simple RSS/Atom:
    - RSS: <item> con <title>, <link>, <pubDate>, <description>
    - Atom: <entry> con <title>, <link href>, <updated>/<published>, <summary>/<content>
    """
    items: list[RssItem] = []

    root = ET.fromstring(feed_xml)

    # Detectar Atom por namespace
    is_atom = "feed" in root.tag.lower()

    if is_atom:
        ns = {"atom": root.tag.split("}")[0].strip("{")} if "}" in root.tag else {}
        for entry in root.findall(".//atom:entry", ns) if ns else root.findall(".//entry"):
            title = (entry.findtext("atom:title", default="", namespaces=ns) if ns else entry.findtext("title", "")).strip()
            link_el = entry.find("atom:link", ns) if ns else entry.find("link")
            url = ""
            if link_el is not None:
                url = link_el.attrib.get("href") or link_el.attrib.get("src") or ""
            published = (entry.findtext("atom:published", default="", namespaces=ns) if ns else entry.findtext("published", "")) \
                        or (entry.findtext("atom:updated", default="", namespaces=ns) if ns else entry.findtext("updated", ""))
            summary = (entry.findtext("atom:summary", default="", namespaces=ns) if ns else entry.findtext("summary", "")) \
                      or (entry.findtext("atom:content", default="", namespaces=ns) if ns else entry.findtext("content", ""))

            items.append(
                RssItem(
                    title=html_to_text(title),
                    url=url.strip(),
                    source=source_name,
                    published_at=_safe_dt(published),
                    summary_raw=summary or "",
                )
            )
        return items

    # RSS tradicional
    for item in root.findall(".//item"):
        title = (item.findtext("title", "") or "").strip()
        link = (item.findtext("link", "") or "").strip()
        pub = (item.findtext("pubDate", "") or "").strip()
        desc = (item.findtext("description", "") or "").strip()

        items.append(
            RssItem(
                title=html_to_text(title),
                url=link,
                source=source_name,
                published_at=_safe_dt(pub),
                summary_raw=desc,
            )
        )

    return items
