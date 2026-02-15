from __future__ import annotations

import re

def parse_since_to_hours(s: str) -> int:
    """
    Convierte strings tipo '24h', '7d', '48h' a horas.
    """
    s = s.strip().lower()
    m = re.fullmatch(r"(\d+)\s*([hd])", s)
    if not m:
        raise ValueError("Formato --since inválido. Usa por ejemplo 24h o 7d.")
    n = int(m.group(1))
    unit = m.group(2)
    if unit == "h":
        return n
    return n * 24
