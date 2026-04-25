from pathlib import Path

from packages.literature.search import search_literature


def test_literature_search_fallback_is_available() -> None:
    root = Path(__file__).resolve().parents[1]
    query_plan, papers, mode = search_literature(root, force_fallback=True)

    assert mode == "fallback"
    assert query_plan.exact_queries
    assert len(papers) >= 2
    assert papers[0].retrieval_mode == "fallback"

