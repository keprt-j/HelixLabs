from packages.models import ExperimentRun, ProvenanceEvent, ProvenanceReport, ProvenanceReportSection
from packages.research_plans import plan_from_run


def generate_report(run: ExperimentRun, events: list[ProvenanceEvent]) -> ProvenanceReport:
    artifacts = run.artifacts
    plan = plan_from_run(artifacts)
    sections = [
        ProvenanceReportSection(title="Research Goal", content=run.user_goal),
        ProvenanceReportSection(
            title="Parsed Intent",
            content=_compact(artifacts.get("scientific_intent", {})),
        ),
        ProvenanceReportSection(
            title="Prior Work",
            content=f"{plan.already_tested_label} were already tested; {plan.failed_condition_label} previously failed the preservation criterion.",
        ),
        ProvenanceReportSection(
            title="Experiment IR",
            content=f"Compiled a boundary screen for {plan.candidate_values} using controls {plan.controls}.",
        ),
        ProvenanceReportSection(
            title="Execution and Recovery",
            content="Simulated property_predictor_timeout at the middle condition; selected retry_failed_condition.",
        ),
        ProvenanceReportSection(
            title="Schema Repair",
            content="Mapped mn_pct, e_hull, cond_proxy, and stable into the materials_screen_v1 schema.",
        ),
        ProvenanceReportSection(
            title="Result Interpretation",
            content=plan.interpretation.uncertainty,
        ),
        ProvenanceReportSection(
            title="Next Experiment",
            content=f"Boundary screen at {plan.next_values}.",
        ),
    ]
    return ProvenanceReport(
        run_id=run.id,
        title="HelixLabs Experiment Report",
        sections=sections,
        provenance_events=events,
    )


def _compact(value: object) -> str:
    if isinstance(value, dict):
        return "; ".join(f"{key}: {val}" for key, val in list(value.items())[:8])
    return str(value)
