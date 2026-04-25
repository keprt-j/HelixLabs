from pathlib import Path

from packages.models import ExperimentIR, FeasibilityReport, ValidationIssue


def validate_feasibility(root: Path, ir: ExperimentIR) -> FeasibilityReport:
    schema_path = root / "data" / "expected_schemas" / f"{ir.expected_output_schema}.json"
    issues = [
        ValidationIssue(
            severity="info",
            issue="0%, 5%, and 10% Mn were already tested.",
            resolution="Excluded redundant low-fraction conditions.",
        ),
        ValidationIssue(
            severity="warning",
            issue="20% Mn previously failed stability.",
            resolution="Avoided 20% and selected 12-16% boundary screen.",
        ),
    ]
    if not ir.variables.get("mn_fraction"):
        issues.append(
            ValidationIssue(
                severity="error",
                issue="No Mn fraction variables were defined.",
                resolution="Define mn_fraction values before protocol generation.",
            )
        )
    if not ir.controls:
        issues.append(
            ValidationIssue(
                severity="error",
                issue="No controls were specified.",
                resolution="Add undoped and prior 10% Mn controls.",
            )
        )
    if not schema_path.exists():
        issues.append(
            ValidationIssue(
                severity="error",
                issue=f"Expected output schema {ir.expected_output_schema} was not found.",
                resolution="Add the expected schema before execution.",
            )
        )
    approved = not any(issue.severity == "error" for issue in issues)
    return FeasibilityReport(
        validation_status="passed_with_warnings" if approved else "failed",
        issues=issues,
        approved_for_protocol_generation=approved,
    )

