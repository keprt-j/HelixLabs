from __future__ import annotations

from pathlib import Path

from packages.literature.crossref_client import CrossrefClient
from packages.literature.deduplicator import dedupe_papers
from packages.literature.query_planner import build_query_plan
from packages.models import LiteratureQueryPlan, RetrievedPaper, ScientificIntent


def search_literature(
    root: Path,
    intent: ScientificIntent | None = None,
    client: CrossrefClient | None = None,
) -> tuple[LiteratureQueryPlan, list[RetrievedPaper], str]:
    query_plan = build_query_plan(intent)
    live_client = client or CrossrefClient()
    papers: list[RetrievedPaper] = []
    for query in [*query_plan.exact_queries, *query_plan.broad_queries, *query_plan.negative_result_queries[:1]]:
        papers.extend(live_client.search(query))
    unique = dedupe_papers(papers)
    retrieval_mode = "live" if unique else "live_no_results"
    return query_plan, unique, retrieval_mode
