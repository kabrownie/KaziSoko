"""PDF advert extraction with conservative, reviewable heuristics."""

from __future__ import annotations

from datetime import datetime, timezone
import re
from typing import Optional

import pdfplumber

from .models import Job

DATE_RE = re.compile(r"\b(20\d{2}[-/]\d{1,2}[-/]\d{1,2})\b")


def extract_pdf(path: str, *, url: str, source_name: str, category: str, location: str) -> Optional[Job]:
    with pdfplumber.open(path) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return None
    deadline = DATE_RE.search(text)
    title = next((line for line in lines if "job" in line.casefold() or "position" in line.casefold()), lines[0])
    organisation = next(
        (line.split(":", 1)[1].strip() for line in lines
         if line.casefold().startswith(("organisation:", "organization:"))),
        source_name,
    )
    return Job(
        title=title[:200],
        organisation=organisation[:200],
        category=category,
        location=location,
        deadline=deadline.group(1).replace("/", "-") if deadline else "",
        source_url=url,
        source_name=source_name,
        scraped_at=datetime.now(timezone.utc).isoformat(),
    )
