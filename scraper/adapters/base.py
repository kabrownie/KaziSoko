"""Shared crawling helpers for polite, resilient adapters."""

from __future__ import annotations

from dataclasses import dataclass
import logging
import time
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

import requests

LOG = logging.getLogger(__name__)
USER_AGENT = "KaziSoko/1.0 (+https://github.com/kabrownie/KaziSoko; public job index)"


@dataclass
class Crawler:
    session: requests.Session
    minimum_delay: float = 1.0
    _last_request: float = 0.0

    @classmethod
    def create(cls) -> "Crawler":
        session = requests.Session()
        session.headers.update({"User-Agent": USER_AGENT, "Accept": "text/html,application/pdf"})
        return cls(session)

    def allowed(self, url: str) -> bool:
        parsed = requests.utils.urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        parser = RobotFileParser(robots_url)
        try:
            parser.read()
        except requests.RequestException:
            LOG.warning("Could not read robots.txt for %s; skipping URL", parsed.netloc)
            return False
        return parser.can_fetch(USER_AGENT, url)

    def get(self, url: str, **kwargs: object) -> requests.Response:
        if not self.allowed(url):
            raise PermissionError(f"robots.txt disallows {url}")
        wait = self.minimum_delay - (time.monotonic() - self._last_request)
        if wait > 0:
            time.sleep(wait)
        response = self.session.get(url, timeout=30, **kwargs)
        self._last_request = time.monotonic()
        if response.status_code not in (403, 429):
            response.raise_for_status()
        return response

    @staticmethod
    def absolute(base: str, href: str) -> str:
        return urljoin(base, href)


def fetch_with_playwright(url: str) -> str:
    """Render a protected page when a static request is challenged."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page(user_agent=USER_AGENT)
            page.goto(url, wait_until="networkidle", timeout=45_000)
            return page.content()
        finally:
            browser.close()
