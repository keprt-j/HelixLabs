from packages.execution.adapters.simulated_lab import RAW_RESULT_CSV
from packages.validation.data_stent import validate_and_repair


def test_data_stent_repairs_drifted_columns() -> None:
    report, repaired = validate_and_repair(RAW_RESULT_CSV)

    assert report.valid is False
    assert report.repair_status == "applied"
    assert [issue.found for issue in report.issues] == ["mn_pct", "e_hull", "cond_proxy", "stable"]
    assert repaired[0].mn_fraction == 0.12
    assert repaired[2].stability_pass is False

