from __future__ import annotations

import urllib.parse
import urllib.request
from pathlib import Path

from packages.literature.query_planner import build_query_plan
from packages.models import LiteratureQueryPlan, RetrievedPaper
from packages.storage import load_json


def search_literature(root: Path, force_fallback: bool = False) -> tuple[LiteratureQueryPlan, list[RetrievedPaper], str]:
    query_plan = build_query_plan()
    if not force_fallback:
        try:
            papers = _crossref_search(query_plan.exact_queries[0])
            if papers:
                # Keep the curated evidence in the returned set so the demo path remains deterministic.
                fallback = _fallback_papers(root)
                return query_plan, _dedupe(papers + fallback), "live_with_cached_context"
        except Exception:
            pass
    return query_plan, _fallback_papers(root), "fallback"


def _crossref_search(query: str) -> list[RetrievedPaper]:
    encoded = urllib.parse.urlencode({"query.title": query, "rows": "3"})
    req = urllib.request.Request(
        f"https://api.crossref.org/works?{encoded}",
        headers={"User-Agent": "HelixLabs MVP (mailto:demo@example.com)"},
    )
    with urllib.request.urlopen(req, timeout=3) as response:
        import json

        payload = json.loads(response.read().decode("utf-8"))
    papers: list[RetrievedPaper] = []
    for idx, item in enumerate(payload.get("message", {}).get("items", []), start=1):
        title = (item.get("title") or ["Untitled Crossref work"])[0]
        abstract = item.get("abstract") or "Crossref metadata result for LiFePO4 manganese cathode query."
        authors = [
            " ".join(part for part in [author.get("given"), author.get("family")] if part)
            for author in item.get("author", [])[:4]
        ] or ["Unknown"]
        year_parts = item.get("published-print") or item.get("published-online") or item.get("created") or {}
        year = (year_parts.get("date-parts") or [[None]])[0][0]
        papers.append(
            RetrievedPaper(
                paper_id=f"CROSSREF-{idx}",
                title=title,
                abstract=abstract,
                authors=authors,
                year=year,
                venue=(item.get("container-title") or ["Crossref"])[0],
                doi=item.get("DOI"),
                url=item.get("URL"),
                source="crossref",
                retrieval_mode="live",
            )
        )
    return papers


def _fallback_papers(root: Path) -> list[RetrievedPaper]:
    return [RetrievedPaper.model_validate(item) for item in load_json(root, "data/sample_literature.json")]


def _dedupe(papers: list[RetrievedPaper]) -> list[RetrievedPaper]:
    seen: set[str] = set()
    unique: list[RetrievedPaper] = []
    for paper in papers:
        key = (paper.doi or paper.title).lower()
        if key not in seen:
            seen.add(key)
            unique.append(paper)
    return unique

