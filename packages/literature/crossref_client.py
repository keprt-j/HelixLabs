from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request

from packages.models import RetrievedPaper


class CrossrefClient:
    def search(self, query: str, rows: int = 3) -> list[RetrievedPaper]:
        params = {"query.bibliographic": query, "rows": str(rows)}
        if os.getenv("CROSSREF_MAILTO"):
            params["mailto"] = os.environ["CROSSREF_MAILTO"]
        encoded = urllib.parse.urlencode(params)
        mailto = os.getenv("CROSSREF_MAILTO", "demo@example.com")
        req = urllib.request.Request(
            f"https://api.crossref.org/works?{encoded}",
            headers={"User-Agent": f"HelixLabs MVP (mailto:{mailto})"},
        )
        with urllib.request.urlopen(req, timeout=3) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return [self._to_paper(index, item) for index, item in enumerate(payload.get("message", {}).get("items", []), start=1)]

    def _to_paper(self, index: int, item: dict) -> RetrievedPaper:
        title = (item.get("title") or ["Untitled Crossref work"])[0]
        abstract = item.get("abstract") or "Crossref metadata result for LiFePO4 manganese cathode query."
        authors = [
            " ".join(part for part in [author.get("given"), author.get("family")] if part)
            for author in item.get("author", [])[:4]
        ] or ["Unknown"]
        year_parts = item.get("published-print") or item.get("published-online") or item.get("created") or {}
        year = (year_parts.get("date-parts") or [[None]])[0][0]
        return RetrievedPaper(
            paper_id=f"CROSSREF-{index}",
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
