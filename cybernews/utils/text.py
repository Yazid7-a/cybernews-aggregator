from __future__ import annotations

import html
import re
from bs4 import BeautifulSoup

WHITESPACE_RE = re.compile(r"\s+")
SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def clean_whitespace(s: str) -> str:
    """Normaliza espacios en blanco y recorta."""
    return WHITESPACE_RE.sub(" ", (s or "")).strip()


def strip_html(text: str) -> str:
    """Elimina tags HTML de forma simple."""
    if not text:
        return ""
    return re.sub(r"<[^>]+>", "", str(text))


def html_to_text(raw: str) -> str:
    """
    Convierte HTML/entidades a texto plano y arregla entidades rotas
    tipo: '&#;x26;#;39;' -> '&#x26;#39;'
    """
    if not raw:
        return ""

    raw = str(raw)

    # Arregla entidades mal escapadas frecuentes en algunos feeds
    raw = raw.replace("&#;x", "&#x").replace("&#;X", "&#X")
    raw = raw.replace("&#;#", "&#")

    raw = html.unescape(raw)
    soup = BeautifulSoup(raw, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    return clean_whitespace(text)


def split_sentences(text: str) -> list[str]:
    """Divide texto en frases (heurística simple)."""
    text = clean_whitespace(text)
    if not text:
        return []
    parts = SENT_SPLIT_RE.split(text)
    return [p.strip() for p in parts if p.strip()]


def clamp_lines(text: str, max_lines: int = 5) -> str:
    """
    Recorta a N líneas.
    - Si ya hay saltos de línea, respeta y recorta por líneas.
    - Si no, recorta por frases.
    """
    if not text:
        return ""

    lines = [ln.strip() for ln in str(text).splitlines() if ln.strip()]
    if len(lines) >= 2:
        return "\n".join(lines[:max_lines])

    parts = split_sentences(str(text))
    if not parts:
        return clean_whitespace(str(text))[:500]
    return "\n".join(parts[:max_lines]).strip()


def top_terms_from_titles(titles: list[str], min_len: int = 4) -> list[tuple[str, int]]:
    """Tendencias simples contando términos repetidos en títulos."""
    stop = {
        "this", "that", "with", "from", "have", "your", "about", "into", "after", "over", "their", "they", "them",
        "the", "and", "for", "are", "was", "were", "has", "had", "you", "its", "in", "on", "to", "of", "a", "an",
        "para", "como", "esta", "este", "sobre", "entre", "pero", "porque", "cuando", "donde",
    }

    counts: dict[str, int] = {}
    for t in titles:
        words = re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9\-]{%d,}" % min_len, str(t))
        for w in words:
            key = w.lower()
            if key in stop:
                continue
            counts[key] = counts.get(key, 0) + 1

    return sorted(counts.items(), key=lambda x: x[1], reverse=True)
