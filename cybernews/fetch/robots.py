from __future__ import annotations

import logging
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

from cybernews.fetch.http_client import HttpClient

log = logging.getLogger("robots")

class RobotsCache:
    def __init__(self, http: HttpClient):
        self._http = http
        self._cache: dict[str, RobotFileParser] = {}

    def allowed(self, url: str, user_agent: str) -> bool:
        p = urlparse(url)
        base = f"{p.scheme}://{p.netloc}"
        if base not in self._cache:
            rp = RobotFileParser()
            robots_url = f"{base}/robots.txt"
            try:
                r = self._http.get(robots_url)
                rp.parse(r.text.splitlines())
                log.debug("robots.txt cargado: %s", robots_url)
            except Exception as e:
                # Si no se puede leer robots, actuamos conservadores: permitimos solo RSS/feeds conocidos,
                # pero para simplicidad aquí permitimos y nos apoyamos en rate limiting.
                log.warning("No pude leer robots.txt (%s): %s", robots_url, e)
                rp = RobotFileParser()
                rp.parse([])
            self._cache[base] = rp

        return self._cache[base].can_fetch(user_agent, url)
