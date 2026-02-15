from __future__ import annotations

import time
from urllib.parse import urlparse

class DomainRateLimiter:
    def __init__(self, rps: float):
        self._min_interval = 1.0 / max(rps, 0.001)
        self._last: dict[str, float] = {}

    def wait(self, url: str) -> None:
        domain = urlparse(url).netloc.lower()
        now = time.time()
        last = self._last.get(domain, 0.0)
        delta = now - last
        if delta < self._min_interval:
            time.sleep(self._min_interval - delta)
        self._last[domain] = time.time()
