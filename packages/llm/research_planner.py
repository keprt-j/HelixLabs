from __future__ import annotations

import json
import os

import httpx
from pydantic import ValidationError

from packages.models import ResearchPlan, SimulatedResultSeed


class LLMPlanningError(RuntimeError):
    pass


def generate_research_plan(user_goal: str) -> ResearchPlan:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise LLMPlanningError("OPENAI_API_KEY is required for broad research planning.")

    model = os.getenv("HELIXLABS_OPENAI_MODEL", "gpt-4.1-mini")
    schema = ResearchPlan.model_json_schema()
    payload = {
        "model": model,
        "input": [
            {
                "role": "system",
                "content": (
                    "You are HelixLabs' experiment compiler. Produce JSON only. "
                    "Convert the user's scientific question into a conservative, auditable experiment plan. "
                    "Use literature-aware language but do not claim real validation. "
                    "Pick numeric prior_tested_values, known_failed_values, candidate_values, and next_values that make sense for the requested variable. "
                    "candidate_values should be a narrowed screen between already-tested and failed regions. "
                    "simulated_results should contain one failing high candidate and at least two passing lower candidates. "
                    "Use generic local simulated metrics if no real assay is specified. "
                    "For the canonical LiFePO4 Mn-doping cathode goal, use variable_name mn_fraction, variable_label Mn, variable_unit %, "
                    "prior_tested_values [0,0.05,0.1], known_failed_values [0.2], candidate_values [0.12,0.14,0.16], "
                    "next_values [0.145,0.15,0.155], drifted columns mn_pct/e_hull/cond_proxy/stable, "
                    "and simulated result variable_value entries 12, 14, and 16 so schema repair demonstrates percent conversion."
                ),
            },
            {"role": "user", "content": user_goal},
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "research_plan",
                "strict": True,
                "schema": schema,
            }
        },
    }
    try:
        with httpx.Client(timeout=45) as client:
            response = client.post(
                "https://api.openai.com/v1/responses",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
        response.raise_for_status()
        data = response.json()
        text = data.get("output_text") or _extract_output_text(data)
        if not text:
            raise LLMPlanningError("OpenAI response did not include output_text.")
        return _normalize_research_plan(ResearchPlan.model_validate(json.loads(text)), user_goal)
    except (httpx.HTTPError, json.JSONDecodeError, ValidationError) as exc:
        raise LLMPlanningError(f"Could not generate a valid research plan: {exc}") from exc


def _extract_output_text(data: dict) -> str:
    chunks: list[str] = []
    for item in data.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                chunks.append(content["text"])
    return "".join(chunks)


def _normalize_research_plan(plan: ResearchPlan, user_goal: str) -> ResearchPlan:
    updates = {}
    if plan.variable_unit == "%" and "fraction" in plan.variable_name:
        for field in ["prior_tested_values", "known_failed_values", "candidate_values", "next_values"]:
            values = getattr(plan, field)
            if values and max(values) > 1:
                updates[field] = [value / 100.0 for value in values]
    if _is_canonical_cathode_goal(plan, user_goal):
        updates.update(
            {
                "system": "LiFePO4",
                "intervention": "Mn doping",
                "variable_name": "mn_fraction",
                "variable_label": "Mn",
                "variable_unit": "%",
                "prior_tested_values": [0.0, 0.05, 0.1],
                "known_failed_values": [0.2],
                "candidate_values": [0.12, 0.14, 0.16],
                "next_values": [0.145, 0.15, 0.155],
                "controls": ["undoped_LiFePO4", "prior_10pct_Mn_baseline"],
                "already_tested_label": "0%, 5%, and 10% Mn",
                "failed_condition_label": "20% Mn",
                "gap": "The stability boundary between 10% and 20% Mn remains unresolved.",
                "recommendation": "Run a narrowed Mn boundary screen at 12%, 14%, and 16% rather than repeat known conditions.",
                "protocol_name": "LiFePO4 Mn Boundary Screen",
                "candidate_prefix": "LiFePO4",
                "drifted_variable_column": "mn_pct",
                "drifted_primary_metric_column": "e_hull",
                "drifted_target_metric_column": "cond_proxy",
                "drifted_pass_column": "stable",
                "simulated_results": [
                    SimulatedResultSeed(candidate_id="LiFePO4_12", variable_value=12, primary_metric_value=0.039, target_metric_value=1.18, stability_pass=True),
                    SimulatedResultSeed(candidate_id="LiFePO4_14", variable_value=14, primary_metric_value=0.046, target_metric_value=1.22, stability_pass=True),
                    SimulatedResultSeed(candidate_id="LiFePO4_16", variable_value=16, primary_metric_value=0.055, target_metric_value=1.24, stability_pass=False),
                ],
            }
        )
    return plan.model_copy(update=updates)


def _is_canonical_cathode_goal(plan: ResearchPlan, user_goal: str) -> bool:
    text = f"{user_goal} {plan.system} {plan.intervention}".lower()
    return "lifepo4" in text and "mn" in text and "cathode" in text
