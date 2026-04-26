from __future__ import annotations

import re
from typing import Any

import httpx


class LiteratureRetrieverService:
    CROSSREF_URL = "https://api.crossref.org/works"
    OPENALEX_URL = "https://api.openalex.org/works"

    def retrieve(self, query: str, limit: int = 12) -> list[dict[str, Any]]:
        rows = max(3, min(limit, 25))
        try:
            studies = self._retrieve_crossref(query=query, limit=rows)
            if studies:
                return studies
        except Exception:
            pass
        return self._retrieve_openalex(query=query, limit=rows)

    def _retrieve_crossref(self, query: str, limit: int) -> list[dict[str, Any]]:
        params = {"query.bibliographic": query, "rows": limit}
        headers = {"User-Agent": "HelixLabs/0.2 (https://helixlabs.local; mailto:dev@helixlabs.local)"}
        with httpx.Client(timeout=12.0, follow_redirects=True) as client:
            response = client.get(self.CROSSREF_URL, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

        items = data.get("message", {}).get("items", [])
        return [s for s in (self._from_crossref_item(item) for item in items) if s]

    def _retrieve_openalex(self, query: str, limit: int) -> list[dict[str, Any]]:
        params = {"search": query, "per-page": limit}
        with httpx.Client(timeout=12.0, follow_redirects=True) as client:
            response = client.get(self.OPENALEX_URL, params=params)
            response.raise_for_status()
            data = response.json()

        items = data.get("results", [])
        return [s for s in (self._from_openalex_item(item) for item in items) if s]

    def _from_crossref_item(self, item: dict[str, Any]) -> dict[str, Any] | None:
        title = self._first(item.get("title"))
        doi = item.get("DOI")
        if not title or not doi:
            return None
        year = self._extract_year(item)
        authors = self._extract_authors(item.get("author", []))
        abstract = self._clean_abstract(item.get("abstract"))
        return {
            "title": title,
            "authors": authors,
            "year": year,
            "doi": doi,
            "url": item.get("URL", f"https://doi.org/{doi}"),
            "source": "crossref",
            "abstract": abstract,
            "exists": True,
        }

    def _from_openalex_item(self, item: dict[str, Any]) -> dict[str, Any] | None:
        title = item.get("display_name")
        doi_url = item.get("doi")
        if not isinstance(title, str) or not isinstance(doi_url, str):
            return None
        doi = doi_url.removeprefix("https://doi.org/")
        authorships = item.get("authorships", [])
        authors = ", ".join(
            a.get("author", {}).get("display_name", "")
            for a in authorships[:4]
            if isinstance(a.get("author", {}).get("display_name", ""), str)
            and a.get("author", {}).get("display_name", "")
        )
        abstract = self._openalex_abstract(item.get("abstract_inverted_index", {}))
        return {
            "title": title.strip(),
            "authors": authors,
            "year": item.get("publication_year"),
            "doi": doi,
            "url": doi_url,
            "source": "openalex",
            "abstract": abstract,
            "exists": True,
        }

    @staticmethod
    def _first(values: Any) -> str | None:
        if isinstance(values, list) and values:
            first = values[0]
            if isinstance(first, str):
                return first.strip()
        if isinstance(values, str):
            return values.strip()
        return None

    @staticmethod
    def _extract_year(item: dict[str, Any]) -> int | None:
        for key in ("published-print", "published-online", "created", "issued"):
            date_parts = item.get(key, {}).get("date-parts", [])
            if date_parts and date_parts[0]:
                year = date_parts[0][0]
                if isinstance(year, int):
                    return year
        return None

    @staticmethod
    def _extract_authors(author_list: list[dict[str, Any]]) -> str:
        names: list[str] = []
        for author in author_list[:4]:
            given = str(author.get("given", "")).strip()
            family = str(author.get("family", "")).strip()
            full = " ".join(part for part in [given, family] if part)
            if full:
                names.append(full)
        return ", ".join(names)

    @staticmethod
    def _clean_abstract(raw: Any) -> str:
        if not isinstance(raw, str):
            return ""
        text = re.sub(r"<[^>]+>", " ", raw)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def _openalex_abstract(inverted_index: Any) -> str:
        if not isinstance(inverted_index, dict) or not inverted_index:
            return ""
        pairs: list[tuple[int, str]] = []
        for token, positions in inverted_index.items():
            if not isinstance(token, str) or not isinstance(positions, list):
                continue
            for pos in positions:
                if isinstance(pos, int):
                    pairs.append((pos, token))
        pairs.sort(key=lambda x: x[0])
        words = [token for _, token in pairs]
        return " ".join(words[:220])
