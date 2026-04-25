from pathlib import Path

from packages.models import ExperimentIR, FeasibilityReport, ResearchPlan, ValidationIssue


def validate_feasibility(root: Path, ir: ExperimentIR, plan: ResearchPlan) -> FeasibilityReport:
    schema_path = root / "data" / "expected_schemas" / f"{ir.expected_output_schema}.json"
    issues = [
        ValidationIssue(
            severity="info",
            issue=f"{plan.already_tested_label} were already tested.",
            resolution="Excluded redundant low-fraction conditions.",
        ),
        ValidationIssue(
            severity="warning",
            issue=f"{plan.failed_condition_label} previously failed the preservation criterion.",
            resolution=plan.recommendation,
        ),
    ]
    if not next(iter(ir.variables.values()), []):
        issues.append(
            ValidationIssue(
                severity="error",
                issue=f"No {plan.variable_label} variables were defined.",
                resolution="Define screen values before protocol generation.",
            )
        )
    if not ir.controls:
        issues.append(
            ValidationIssue(
                severity="error",
                issue="No controls were specified.",
                resolution="Add baseline and prior-reference controls.",
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
