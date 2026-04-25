from __future__ import annotations

import re

from packages.models import RetrievedPaper


def dedupe_papers(papers: list[RetrievedPaper]) -> list[RetrievedPaper]:
    seen: set[str] = set()
    unique: list[RetrievedPaper] = []
    for paper in papers:
        key = _dedupe_key(paper)
        if key not in seen:
            seen.add(key)
            unique.append(paper)
    return unique


def _dedupe_key(paper: RetrievedPaper) -> str:
    if paper.doi:
        return f"doi:{paper.doi.lower().strip()}"
    return f"title:{re.sub(r'[^a-z0-9]+', ' ', paper.title.lower()).strip()}"
