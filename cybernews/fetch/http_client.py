from __future__ import annotations

import logging
import requests

log = logging.getLogger("http")

class HttpClient:
    def __init__(self, user_agent: str, timeout_s: int):
        self._ua = user_agent
        self._timeout = timeout_s
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": self._ua})

    def get(self, url: str) -> requests.Response:
        log.debug("GET %s", url)
        r = self._session.get(url, timeout=self._timeout, allow_redirects=True)
        r.raise_for_status()
        return r
