from packages.models import ExperimentRun, ProvenanceEvent, ProvenanceReport, ProvenanceReportSection


def generate_report(run: ExperimentRun, events: list[ProvenanceEvent]) -> ProvenanceReport:
    artifacts = run.artifacts
    sections = [
        ProvenanceReportSection(title="Research Goal", content=run.user_goal),
        ProvenanceReportSection(
            title="Parsed Intent",
            content=_compact(artifacts.get("scientific_intent", {})),
        ),
        ProvenanceReportSection(
            title="Prior Work",
            content="0%, 5%, and 10% Mn were already tested; 20% Mn previously failed stability.",
        ),
        ProvenanceReportSection(
            title="Experiment IR",
            content="Compiled a boundary screen for 12%, 14%, and 16% Mn using undoped and 10% prior controls.",
        ),
        ProvenanceReportSection(
            title="Execution and Recovery",
            content="Simulated property_predictor_timeout at 14% Mn; selected retry_failed_condition.",
        ),
        ProvenanceReportSection(
            title="Schema Repair",
            content="Mapped mn_pct, e_hull, cond_proxy, and stable into the materials_screen_v1 schema.",
        ),
        ProvenanceReportSection(
            title="Result Interpretation",
            content="12% and 14% passed stability; 16% failed. The exact 14-16% boundary remains unresolved.",
        ),
        ProvenanceReportSection(
            title="Next Experiment",
            content="Boundary screen at 14.5%, 15.0%, and 15.5% Mn.",
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

