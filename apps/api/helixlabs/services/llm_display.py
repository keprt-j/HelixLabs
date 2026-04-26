from __future__ import annotations

import html
import json
import os
from pathlib import Path
import re
from typing import Any

from openai import APIError, OpenAI

from helixlabs.domain.models import RunRecord


class DisplayTextService:
    """Creates persisted, judge-readable display text for dense pipeline artifacts."""

    def __init__(self, model: str | None = None) -> None:
        self._model = model or os.getenv("HELIXLABS_OPENAI_MODEL", "gpt-4.1-mini")

    def polish_claim_graph(
        self,
        *,
        run: RunRecord,
        claim_graph: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        fallback = self._fallback_claim_graph(claim_graph)
        client = self._client()
        if client is None:
            return fallback

        try:
            response = client.responses.create(
                model=self._model,
                input=(
                    "You are editing scientific claim graph text for a hackathon dashboard. "
                    "Return JSON only. Make the claims readable, specific, and plain text. "
                    "Do not invent citations or unsupported facts. Strip HTML/subscript markup. "
                    "Avoid token-list phrasing. Keep each statement under 220 characters.\n"
                    f"User goal: {run.user_goal}\n"
                    f"Current claim graph: {json.dumps(claim_graph)}\n"
                    f"Context: {json.dumps(context)}\n"
                    "Required JSON shape: "
                    "{display_main_claim:string, display_weakest_claim:string, "
                    "display_next_target:string, display_hypotheses:[{id,title,statement,rationale}]}"
                ),
                temperature=0.1,
                max_output_tokens=900,
            )
            data = self._json_object(response.output_text)
            return self._normalize_claim_display(data, fallback)
        except (APIError, ValueError, json.JSONDecodeError, TypeError):
            return fallback

    def summarize_pipeline_section(
        self,
        *,
        run: RunRecord,
        section: str,
        section_json: dict[str, Any],
    ) -> dict[str, str]:
        generated_at = RunRecord.now_iso()
        client = self._client()
        fallback = {
            "summary": self._fallback_section_summary(section=section, section_json=section_json),
            "generated_at": generated_at,
            "source": "local_contextual_fallback",
        }
        if client is None:
            return fallback

        try:
            provenance = [
                {"event_type": event.event_type, "category": event.category, "message": event.message}
                for event in run.provenance[-10:]
            ]
            response = client.responses.create(
                model=self._model,
                input=(
                    "You summarize HelixLabs pipeline JSON for judges. Return one JSON object only, with this exact shape: "
                    "{\"summary\":\"...\"}. The summary must be specific to the provided JSON, not a generic status. "
                    "Mention concrete values, artifacts, decisions, resources, result patterns, recommendations, or provenance "
                    "counts that appear in the JSON. Explain what happened, why it matters, and what decision/output was produced. "
                    "Use 2-4 concise sentences. Do not overclaim scientific validity.\n"
                    f"Section: {section}\n"
                    f"Run state: {run.state.value}\n"
                    f"User goal: {run.user_goal}\n"
                    f"Recent provenance: {json.dumps(provenance)}\n"
                    f"Section JSON: {json.dumps(section_json, default=str)[:12000]}"
                ),
                temperature=0.2,
                max_output_tokens=280,
            )
            data = self._json_object(response.output_text)
            summary = self._clean_text(str(data.get("summary", "")))
            if not summary:
                return fallback
            return {"summary": summary[:900], "generated_at": generated_at, "source": "openai"}
        except (APIError, ValueError, json.JSONDecodeError, TypeError):
            return {
                "summary": self._fallback_section_summary(section=section, section_json=section_json),
                "generated_at": generated_at,
                "source": "local_contextual_fallback",
            }

    def summarize_json_artifact(
        self,
        *,
        run: RunRecord,
        artifact_name: str,
        artifact_json: dict[str, Any],
    ) -> dict[str, str]:
        generated_at = RunRecord.now_iso()
        fallback = {
            "summary": self._fallback_artifact_summary(artifact_name=artifact_name, artifact_json=artifact_json),
            "generated_at": generated_at,
            "source": "local_contextual_fallback",
        }
        client = self._client()
        if client is None:
            return fallback

        try:
            provenance = [
                {"event_type": event.event_type, "category": event.category, "message": event.message}
                for event in run.provenance[-8:]
            ]
            response = client.responses.create(
                model=self._model,
                input=(
                    "You summarize one HelixLabs JSON artifact for a dashboard. Return one JSON object only, "
                    "with this exact shape: {\"summary\":\"...\"}. The summary must be specific to the artifact JSON. "
                    "Mention concrete fields, counts, decisions, warnings, resource allocations, recovery choices, "
                    "validation mappings, or result values that appear in the artifact. Use 1-3 concise sentences. "
                    "Do not overclaim scientific validity.\n"
                    f"Artifact name: {artifact_name}\n"
                    f"Run state: {run.state.value}\n"
                    f"User goal: {run.user_goal}\n"
                    f"Recent provenance: {json.dumps(provenance)}\n"
                    f"Artifact JSON: {json.dumps(artifact_json, default=str)[:10000]}"
                ),
                temperature=0.2,
                max_output_tokens=240,
            )
            data = self._json_object(response.output_text)
            summary = self._clean_text(str(data.get("summary", "")))
            if not summary:
                return fallback
            return {"summary": summary[:700], "generated_at": generated_at, "source": "openai"}
        except (APIError, ValueError, json.JSONDecodeError, TypeError):
            return fallback

    def _client(self) -> OpenAI | None:
        self._load_env_file()
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        return OpenAI(api_key=api_key) if api_key else None

    @classmethod
    def _fallback_claim_graph(cls, claim_graph: dict[str, Any]) -> dict[str, Any]:
        main = cls._clean_claim(
            str(claim_graph.get("main_claim", "")),
            "The evidence suggests a testable relationship between the chosen intervention and the target outcome.",
        )
        weak = cls._clean_claim(
            str(claim_graph.get("weakest_claim", "")),
            "The least-certain claim is whether that relationship holds at the boundary conditions that matter for this run.",
        )
        target = cls._clean_claim(
            str(claim_graph.get("next_target", "")),
            "The next target is to test boundary settings that distinguish improvement from instability or weak performance.",
        )
        display_hypotheses: list[dict[str, str]] = []
        for idx, raw in enumerate(list(claim_graph.get("hypotheses") or []), start=1):
            if not isinstance(raw, dict):
                continue
            hyp_id = str(raw.get("id") or f"H{idx}")
            title = cls._clean_text(str(raw.get("title") or f"Hypothesis {idx}"))
            statement = cls._clean_claim(str(raw.get("statement") or ""), target)
            display_hypotheses.append(
                {
                    "id": hyp_id,
                    "title": title,
                    "statement": statement,
                    "rationale": "Prepared as a plain-language, evidence-aware hypothesis for planning review.",
                }
            )
        return {
            "display_main_claim": main,
            "display_weakest_claim": weak,
            "display_next_target": target,
            "display_hypotheses": display_hypotheses,
        }

    @classmethod
    def _normalize_claim_display(cls, data: dict[str, Any], fallback: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(fallback)
        for key in ("display_main_claim", "display_weakest_claim", "display_next_target"):
            normalized[key] = cls._clean_claim(str(data.get(key, "")), str(fallback[key]))
        raw_hypotheses = data.get("display_hypotheses")
        if isinstance(raw_hypotheses, list):
            hypotheses: list[dict[str, str]] = []
            for idx, raw in enumerate(raw_hypotheses, start=1):
                if not isinstance(raw, dict):
                    continue
                statement = cls._clean_claim(str(raw.get("statement") or ""), "")
                if not statement:
                    continue
                hypotheses.append(
                    {
                        "id": cls._clean_text(str(raw.get("id") or f"H{idx}")),
                        "title": cls._clean_text(str(raw.get("title") or f"Hypothesis {idx}")),
                        "statement": statement,
                        "rationale": cls._clean_text(str(raw.get("rationale") or "")),
                    }
                )
            if hypotheses:
                normalized["display_hypotheses"] = hypotheses
        return normalized

    @classmethod
    def _clean_claim(cls, text: str, fallback: str) -> str:
        cleaned = cls._clean_text(text)
        token_list = re.search(r"evidence indicates ([a-z0-9,\s-]{8,80}) strongly influences", cleaned, flags=re.I)
        if token_list and "," in token_list.group(1):
            return fallback
        if len(cleaned.split()) < 4:
            return fallback
        return cleaned

    @staticmethod
    def _clean_text(text: str) -> str:
        cleaned = html.unescape(text or "")
        cleaned = re.sub(r"<\s*sub\s*>(.*?)<\s*/\s*sub\s*>", r"\1", cleaned, flags=re.I)
        cleaned = re.sub(r"<[^>]+>", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip(" \t\r\n\"'")
        return cleaned

    @staticmethod
    def _json_object(text: str) -> dict[str, Any]:
        raw = text.strip()
        if raw.startswith("```"):
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
        if not raw.startswith("{"):
            match = re.search(r"\{.*\}", raw, flags=re.S)
            if match:
                raw = match.group(0)
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("LLM did not return a JSON object")
        return data

    @staticmethod
    def _fallback_section_summary(section: str, section_json: dict[str, Any]) -> str:
        if not section_json:
            return f"No {section} pipeline data has been generated yet."
        artifacts = section_json.get("artifacts") if isinstance(section_json.get("artifacts"), dict) else {}
        pipeline = section_json.get("pipeline") if isinstance(section_json.get("pipeline"), dict) else {}
        if section == "planning":
            ir = artifacts.get("experiment_ir") if isinstance(artifacts.get("experiment_ir"), dict) else {}
            schedule = artifacts.get("schedule") if isinstance(artifacts.get("schedule"), dict) else {}
            value = artifacts.get("value_score") if isinstance(artifacts.get("value_score"), dict) else {}
            conditions = ir.get("conditions") if isinstance(ir.get("conditions"), list) else []
            resources = schedule.get("resources") or schedule.get("resource_schedule") or pipeline.get("schedule")
            metrics = ir.get("metrics") or ir.get("measurable_outputs") or []
            return (
                f"Planning compiled {len(conditions)} experiment conditions with metrics {DisplayTextService._compact(metrics)}. "
                f"The value model reports {DisplayTextService._compact(value)} and the scheduler allocated "
                f"{DisplayTextService._compact(resources)}."
            )
        if section == "runtime":
            execution = artifacts.get("execution_log") if isinstance(artifacts.get("execution_log"), dict) else {}
            recovery = artifacts.get("failure_recovery_plan") if isinstance(artifacts.get("failure_recovery_plan"), dict) else {}
            validation = artifacts.get("validation_report") if isinstance(artifacts.get("validation_report"), dict) else {}
            interpretation = artifacts.get("interpretation") if isinstance(artifacts.get("interpretation"), dict) else {}
            return (
                f"Runtime captured execution status {DisplayTextService._compact(execution.get('status') or execution.get('events'))}, "
                f"used recovery action {DisplayTextService._compact(recovery.get('selected_action') or recovery)}, and validation reported "
                f"{DisplayTextService._compact(validation)}. Interpretation concluded {DisplayTextService._compact(interpretation)}."
            )
        recommendation = artifacts.get("next_experiment_recommendation")
        report = artifacts.get("report") if isinstance(artifacts.get("report"), dict) else {}
        memory = artifacts.get("memory_update") if isinstance(artifacts.get("memory_update"), dict) else {}
        provenance = artifacts.get("provenance") if isinstance(artifacts.get("provenance"), list) else []
        return (
            f"Outcomes recommend {DisplayTextService._compact(recommendation)} and generated report fields "
            f"{DisplayTextService._compact(list(report.keys()))}. Memory update recorded {DisplayTextService._compact(memory)} "
            f"with {len(provenance)} provenance events attached."
        )

    @staticmethod
    def _fallback_artifact_summary(artifact_name: str, artifact_json: dict[str, Any]) -> str:
        if not artifact_json:
            return f"No {artifact_name.replace('_', ' ')} JSON is available yet."
        if artifact_name == "experiment_ir":
            conditions = artifact_json.get("conditions") if isinstance(artifact_json.get("conditions"), list) else []
            metrics = artifact_json.get("metrics") or artifact_json.get("measurable_outputs") or []
            controls = artifact_json.get("controls") or []
            return (
                f"Experiment IR defines {len(conditions)} conditions, metrics {DisplayTextService._compact(metrics)}, "
                f"and controls {DisplayTextService._compact(controls)}."
            )
        if artifact_name == "feasibility_report":
            status = artifact_json.get("validation_status") or artifact_json.get("status")
            issues = artifact_json.get("issues") if isinstance(artifact_json.get("issues"), list) else []
            return f"Feasibility status is {DisplayTextService._compact(status)} with {len(issues)} issue or warning entries."
        if artifact_name == "value_score":
            return f"Value scoring produced {DisplayTextService._compact(artifact_json)}."
        if artifact_name == "protocol":
            steps = artifact_json.get("steps") if isinstance(artifact_json.get("steps"), list) else []
            return f"Protocol contains {len(steps)} steps and fields {DisplayTextService._compact(list(artifact_json.keys()))}."
        if artifact_name == "schedule":
            sid = artifact_json.get("schedule_id")
            duration = artifact_json.get("total_duration_hours")
            util = artifact_json.get("resource_utilization_pct")
            return f"Schedule {DisplayTextService._compact(sid)} allocates {DisplayTextService._compact(duration)} hours at {DisplayTextService._compact(util)}% utilization."
        if artifact_name == "execution_log":
            measurements = artifact_json.get("measurements") if isinstance(artifact_json.get("measurements"), list) else []
            status = artifact_json.get("status")
            failures = artifact_json.get("failures") or artifact_json.get("failure")
            return f"Execution status is {DisplayTextService._compact(status)} with {len(measurements)} measurements and failure signal {DisplayTextService._compact(failures)}."
        if artifact_name == "failure_recovery_plan":
            action = artifact_json.get("selected_action") or artifact_json.get("action")
            reason = artifact_json.get("reason") or artifact_json.get("rationale")
            return f"Recovery selected {DisplayTextService._compact(action)} because {DisplayTextService._compact(reason)}."
        if artifact_name == "validation_report":
            status = artifact_json.get("validation_status") or artifact_json.get("status")
            mapped = artifact_json.get("mapped_columns") or artifact_json.get("column_mapping")
            records = artifact_json.get("validated_records")
            return f"Data validation status is {DisplayTextService._compact(status)} with {DisplayTextService._compact(records)} validated records and mappings {DisplayTextService._compact(mapped)}."
        if artifact_name == "interpretation":
            return f"Interpretation summarized {DisplayTextService._compact(artifact_json)}."
        return f"{artifact_name.replace('_', ' ').title()} includes fields {DisplayTextService._compact(list(artifact_json.keys()))}."

    @staticmethod
    def _compact(value: Any, limit: int = 220) -> str:
        if value in (None, "", [], {}):
            return "no specific value"
        text = DisplayTextService._clean_text(json.dumps(value, default=str) if not isinstance(value, str) else value)
        return text[: limit - 1] + "..." if len(text) > limit else text

    @staticmethod
    def _load_env_file() -> None:
        if os.getenv("OPENAI_API_KEY", "").strip():
            return
        candidates: list[Path] = []
        cwd = Path.cwd()
        candidates.extend(parent / ".env" for parent in [cwd, *cwd.parents])
        here = Path(__file__).resolve()
        candidates.extend(parent / ".env" for parent in here.parents)
        for path in candidates:
            if not path.exists() or not path.is_file():
                continue
            for line in path.read_text(encoding="utf-8").splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith("#") or "=" not in stripped:
                    continue
                key, value = stripped.split("=", 1)
                key = key.strip()
                if key and key not in os.environ:
                    os.environ[key] = value.strip().strip("\"'")
            if os.getenv("OPENAI_API_KEY", "").strip():
                return
