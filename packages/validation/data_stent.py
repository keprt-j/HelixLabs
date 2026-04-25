from __future__ import annotations

import csv
import io
from typing import Any

from packages.models import RepairedResult, ResearchPlan, ResultValidationIssue, ValidationReport


def validate_and_repair(raw_csv: str, plan: ResearchPlan | None = None) -> tuple[ValidationReport, list[Any]]:
    rows = list(csv.DictReader(io.StringIO(raw_csv)))
    if plan is not None:
        return _validate_and_repair_plan(rows, plan)
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


def _validate_and_repair_plan(rows: list[dict[str, str]], plan: ResearchPlan) -> tuple[ValidationReport, list[dict[str, Any]]]:
    variable_name = plan.variable_name
    primary_metric = plan.success_metrics[0]
    secondary_metric = plan.success_metrics[1]
    pass_metric = "stability_pass"
    issues = [
        ResultValidationIssue(
            type="column_name_mismatch",
            expected=variable_name,
            found=plan.drifted_variable_column,
            repair=f"map {plan.drifted_variable_column} to {variable_name}",
        ),
        ResultValidationIssue(
            type="column_name_mismatch",
            expected=primary_metric,
            found=plan.drifted_primary_metric_column,
            repair=f"map {plan.drifted_primary_metric_column} to {primary_metric}",
        ),
        ResultValidationIssue(
            type="column_name_mismatch",
            expected=secondary_metric,
            found=plan.drifted_target_metric_column,
            repair=f"map {plan.drifted_target_metric_column} to {secondary_metric}",
        ),
        ResultValidationIssue(
            type="column_name_mismatch",
            expected=pass_metric,
            found=plan.drifted_pass_column,
            repair=f"map {plan.drifted_pass_column} to {pass_metric}",
        ),
    ]
    repaired = []
    for row in rows:
        variable_raw = float(row[plan.drifted_variable_column])
        variable_value = variable_raw / 100.0 if variable_raw > 1 and plan.variable_unit == "%" else variable_raw
        repaired.append(
            {
                "candidate_id": row["candidate_id"],
                variable_name: variable_value,
                primary_metric: float(row[plan.drifted_primary_metric_column]),
                secondary_metric: float(row[plan.drifted_target_metric_column]),
                pass_metric: row[plan.drifted_pass_column].strip().lower() == "true",
            }
        )
    return ValidationReport(valid=False, issues=issues, repair_status="applied"), repaired
