from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class PageContent:
    url: str
    text: str
    suspicious: bool = False
    suspicious_reasons: List[str] = field(default_factory=list)


@dataclass
class ResearchResult:
    goal: str
    summary: str
    key_points: List[str]
    citations: List[str]
    blocked_urls: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

