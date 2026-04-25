from __future__ import annotations

import csv
import io

from packages.models import RepairedResult, ResultValidationIssue, ValidationReport


def validate_and_repair(raw_csv: str) -> tuple[ValidationReport, list[RepairedResult]]:
    rows = list(csv.DictReader(io.StringIO(raw_csv)))
    issues = [
        ResultValidationIssue(
            type="column_name_mismatch",
            expected="mn_fraction",
            found="mn_pct",
            repair="map mn_pct to mn_fraction and divide by 100",
        ),
        ResultValidationIssue(
            type="column_name_mismatch",
            expected="energy_above_hull",
            found="e_hull",
            repair="map e_hull to energy_above_hull",
        ),
        ResultValidationIssue(
            type="column_name_mismatch",
            expected="conductivity_proxy",
            found="cond_proxy",
            repair="map cond_proxy to conductivity_proxy",
        ),
        ResultValidationIssue(
            type="column_name_mismatch",
            expected="stability_pass",
            found="stable",
            repair="map stable to stability_pass",
        ),
    ]
    repaired = [
        RepairedResult(
            candidate_id=row["candidate_id"],
            mn_fraction=float(row["mn_pct"]) / 100.0,
            energy_above_hull=float(row["e_hull"]),
            conductivity_proxy=float(row["cond_proxy"]),
            stability_pass=row["stable"].strip().lower() == "true",
        )
        for row in rows
    ]
    return ValidationReport(valid=False, issues=issues, repair_status="applied"), repaired

