from packages.models import FailureRecoveryPlan, RecoveryOption, ResearchPlan


def build_recovery_plan(plan: ResearchPlan | None = None) -> FailureRecoveryPlan:
    condition = "14_percent_Mn"
    if plan:
        middle = plan.candidate_values[len(plan.candidate_values) // 2]
        condition = f"{plan.variable_name}_{middle:g}"
    return FailureRecoveryPlan(
        failure_type="property_predictor_timeout",
        affected_step="S4",
        affected_condition=condition,
        recovery_options=[
            RecoveryOption(action="retry_failed_condition", cost_minutes=8, data_loss="none", score=0.91),
            RecoveryOption(action="skip_failed_condition", cost_minutes=0, data_loss=f"{condition}_missing", score=0.42),
            RecoveryOption(action="rerun_full_experiment", cost_minutes=65, data_loss="none", score=0.28),
        ],
        selected_recovery="retry_failed_condition",
    )
