from __future__ import annotations

from typing import Any

from packages.models import ResearchPlan


def plan_from_run(artifacts: dict[str, Any]) -> ResearchPlan:
    if "research_plan" not in artifacts:
        raise KeyError("research_plan")
    return ResearchPlan.model_validate(artifacts["research_plan"])


def values_to_conditions(values: list[float], variable_label: str, variable_unit: str = "") -> list[str]:
    unit = variable_unit.strip()
    label = variable_label.strip()
    if unit == "%":
        return [f"{value * 100:g}% {label}" if value <= 1 else f"{value:g}% {label}" for value in values]
    if label.lower() == "ph":
        return [f"pH {value:g}" for value in values]
    suffix = f" {unit}" if unit else ""
    return [f"{label} {value:g}{suffix}" for value in values]


def condition_label(value: float, variable_label: str, variable_unit: str = "") -> str:
    return values_to_conditions([value], variable_label, variable_unit)[0]
