from pathlib import Path

from packages.literature.search import search_literature
from packages.models import RetrievedPaper


class FakeCrossrefClient:
    def search(self, query: str) -> list[RetrievedPaper]:
        return [
            RetrievedPaper(
                paper_id=f"TEST-{abs(hash(query))}",
                title="Live metadata result for cathode boundary screen",
                abstract="Crossref-style live metadata result.",
                authors=["A. Researcher"],
                year=2025,
                venue="Test",
                doi="10.0000/live-result",
                url=None,
                source="crossref",
                retrieval_mode="live",
            )
        ]


def test_literature_search_uses_live_client_and_deduplicates() -> None:
    root = Path(__file__).resolve().parents[1]
    query_plan, papers, mode = search_literature(root, client=FakeCrossrefClient())

    assert mode == "live"
    assert query_plan.exact_queries
    assert len(papers) == 1
    assert papers[0].retrieval_mode == "live"
