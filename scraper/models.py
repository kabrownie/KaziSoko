"""Canonical job model and deterministic identifiers."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import re
from typing import Any


COUNTIES = {
    "nairobi": "Nairobi",
    "mombasa": "Mombasa",
    "kiambu": "Kiambu",
    "nakuru": "Nakuru",
    "kisumu": "Kisumu",
    "uasin gishu": "Uasin Gishu",
}


def normalise(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).casefold()


def normalise_county(value: str) -> str:
    key = normalise(value).replace(" county", "")
    return COUNTIES.get(key, value.strip())


@dataclass(slots=True)
class Job:
    title: str
    organisation: str
    category: str
    location: str
    deadline: str
    source_url: str
    source_name: str
    scraped_at: str
    id: str = ""

    def __post_init__(self) -> None:
        self.location = normalise_county(self.location)
        if not self.id:
            identity = "|".join((normalise(self.title), normalise(self.organisation), self.deadline))
            self.id = sha256(identity.encode("utf-8")).hexdigest()

    def completeness(self) -> int:
        return sum(bool(getattr(self, field)) for field in (
            "title", "organisation", "category", "location", "deadline",
            "source_url", "source_name", "scraped_at",
        ))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
