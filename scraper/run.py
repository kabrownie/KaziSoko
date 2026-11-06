"""Run adapters, merge records, and write the static data file."""

from __future__ import annotations

import argparse
from datetime import date
import json
import logging
from pathlib import Path

from .adapters.base import Crawler
from .adapters.gaa import crawl as crawl_gaa
from .models import Job

LOG = logging.getLogger(__name__)


def merge_jobs(jobs: list[Job]) -> list[dict]:
    merged: dict[str, Job] = {}
    for job in jobs:
        current = merged.get(job.id)
        if current is None or job.completeness() > current.completeness():
            merged[job.id] = job
    today = date.today().isoformat()
    return sorted(
        (job.to_dict() for job in merged.values() if not job.deadline or job.deadline >= today),
        key=lambda job: (job["deadline"] or "9999-12-31", job["title"].casefold()),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("site/public/data/jobs.json"))
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    jobs = list(crawl_gaa(Crawler.create()))
    records = merge_jobs(jobs)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    LOG.info("Wrote %d jobs to %s", len(records), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
