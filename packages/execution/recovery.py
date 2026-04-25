from packages.models import FailureRecoveryPlan, RecoveryOption


def build_recovery_plan() -> FailureRecoveryPlan:
    return FailureRecoveryPlan(
        failure_type="property_predictor_timeout",
        affected_step="S4",
        affected_condition="14_percent_Mn",
        recovery_options=[
            RecoveryOption(action="retry_failed_condition", cost_minutes=8, data_loss="none", score=0.91),
            RecoveryOption(action="skip_failed_condition", cost_minutes=0, data_loss="14_percent_Mn_missing", score=0.42),
            RecoveryOption(action="rerun_full_experiment", cost_minutes=65, data_loss="none", score=0.28),
        ],
        selected_recovery="retry_failed_condition",
    )

