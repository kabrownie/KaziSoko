"""Adapter for the Government Advertising Agency public notices."""

from __future__ import annotations

from datetime import datetime, timezone
import logging
import re
from typing import Iterator

from bs4 import BeautifulSoup

from ..models import Job
from .base import Crawler, fetch_with_playwright

LOG = logging.getLogger(__name__)
URL = "https://gaa.go.ke/"
DATE_RE = re.compile(r"(20\d{2}[-/]\d{1,2}[-/]\d{1,2})")


def crawl(crawler: Crawler) -> Iterator[Job]:
    response = crawler.get(URL)
    html = response.text
    if "cloudflare" in html.casefold() or response.status_code in (403, 429):
        LOG.info("GAA appears protected; retrying with Playwright")
        html = fetch_with_playwright(URL)
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    for link in soup.select("a[href]"):
        text = " ".join(link.stripped_strings)
        href = crawler.absolute(URL, link["href"])
        if not text or not any(word in text.casefold() for word in ("vacan", "job", "career", "recruit")):
            continue
        deadline_match = DATE_RE.search(text)
        yield Job(
            title=text[:200],
            organisation="Government Advertising Agency",
            category="National Government",
            location="Kenya",
            deadline=deadline_match.group(1).replace("/", "-") if deadline_match else "",
            source_url=href,
            source_name="Government Advertising Agency",
            scraped_at=scraped_at,
        )
