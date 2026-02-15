from __future__ import annotations

import math
import re
from collections import Counter

from cybernews.summarize.base import Summarizer
from cybernews.utils.text import split_sentences, clean_whitespace

WORD_RE = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9\-]{3,}")

class ExtractiveSummarizer(Summarizer):
    """
    Fallback extractivo simple (sin dependencias): rankea frases por TF (frecuencia) normalizada.
    """
    def __init__(self, max_lines: int = 5):
        self.max_lines = max_lines

    def summarize(self, text: str) -> str:
        text = clean_whitespace(text or "")
        if not text:
            return ""

        sentences = split_sentences(text)
        if not sentences:
            return text[:280]

        words = [w.lower() for w in WORD_RE.findall(text)]
        if not words:
            return " ".join(sentences[: min(3, len(sentences))])

        freq = Counter(words)
        maxf = max(freq.values()) or 1

        scored: list[tuple[int, float]] = []
        for i, s in enumerate(sentences):
            ws = [w.lower() for w in WORD_RE.findall(s)]
            if not ws:
                continue
            score = sum((freq[w] / maxf) for w in ws)
            score = score / math.sqrt(len(ws))
            scored.append((i, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        pick = sorted(scored[: self.max_lines], key=lambda x: x[0])

        out = [sentences[i] for i, _ in pick]
        # 3–5 líneas aproximado: devolvemos en un bloque compacto
        return "\n".join(out[: self.max_lines]).strip()
