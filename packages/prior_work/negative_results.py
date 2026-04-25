from pathlib import Path

from packages.models import NegativeResult
from packages.storage import load_json


def find_negative_results(root: Path) -> list[NegativeResult]:
    return [NegativeResult.model_validate(item) for item in load_json(root, "data/sample_negative_results.json")]

