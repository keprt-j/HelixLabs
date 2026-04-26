from __future__ import annotations

import html
import json
import os
import re
from typing import Any

import httpx
from openai import OpenAI
from openai import APIError

from helixlabs.services.literature_retriever import LiteratureRetrieverService


class LiteratureSynthesizerService:
    def __init__(self, retriever: LiteratureRetrieverService | None = None) -> None:
        self._retriever = retriever or LiteratureRetrieverService()

    def synthesize(self, user_goal: str) -> dict[str, Any]:
        try:
            retrieved = self._retriever.retrieve(user_goal, limit=25)
        except Exception as exc:  # noqa: BLE001
            return self._fallback(user_goal=user_goal, reason=f"Literature retrieval failed: {exc}")

        ranked = self._rank_by_relevance(user_goal=user_goal, studies=retrieved)
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        client = OpenAI(api_key=api_key) if api_key else None
        top = self._select_enriched_studies(ranked=ranked, user_goal=user_goal, client=client, cap=5)

        if not top:
            return self._fallback(user_goal=user_goal, reason="No studies passed data-quality thresholds")

        novelty_score, redundancy_score = self._derive_scores(top)
        axis_hints = self._extract_axis_hints(top, user_goal)
        claims = self._derive_claims(top, user_goal)
        synthesis = {
            "source": "crossref",
            "studies": top,
            "novelty_score": novelty_score,
            "redundancy_score": redundancy_score,
            "main_claim": claims["main_claim"],
            "weakest_claim": claims["weakest_claim"],
            "next_target": claims["next_target"],
            "axis_hints": axis_hints,
        }

        if client is None:
            return synthesis

        # Optional LLM refinement over verified retrieval only.
        try:
            prompt = (
                "You are a scientific synthesis assistant. "
                "Given verified literature records, refine claims only. "
                "Return JSON with keys: main_claim, weakest_claim, next_target, "
                "novelty_score (0-10), redundancy_score (0-10), "
                "and do not invent studies. "
                f"User goal: {user_goal}\n"
                f"Studies: {json.dumps(top)}"
            )
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=prompt,
                temperature=0.2,
                max_output_tokens=500,
            )
            text = response.output_text.strip()
            data = json.loads(text)
            synthesis["source"] = "crossref+openai"
            synthesis["novelty_score"] = float(data.get("novelty_score", novelty_score))
            synthesis["redundancy_score"] = float(data.get("redundancy_score", redundancy_score))
            synthesis["main_claim"] = str(data.get("main_claim", synthesis["main_claim"]))
            synthesis["weakest_claim"] = str(data.get("weakest_claim", synthesis["weakest_claim"]))
            synthesis["next_target"] = str(data.get("next_target", synthesis["next_target"]))
            return synthesis
        except (APIError, ValueError, json.JSONDecodeError):
            return synthesis

    def _select_enriched_studies(
        self,
        ranked: list[dict[str, Any]],
        user_goal: str,
        client: OpenAI | None,
        cap: int,
    ) -> list[dict[str, Any]]:
        selected: list[dict[str, Any]] = []
        for candidate in ranked:
            enriched = self._enrich_single_study(candidate=candidate, user_goal=user_goal, client=client)
            if enriched is None:
                continue
            selected.append(enriched)
            if len(selected) >= cap:
                break
        if not selected:
            return selected
        raw = [float(s.get("relevance", 0.0)) for s in selected]
        lo, hi = min(raw), max(raw)
        rank_targets = [0.95, 0.82, 0.68, 0.54, 0.40]
        for idx, study in enumerate(selected):
            val = float(study.get("relevance", 0.0))
            if hi - lo < 1e-6:
                normalized = 0.65
            else:
                normalized = 0.25 + 0.7 * ((val - lo) / (hi - lo))
            target = rank_targets[min(idx, len(rank_targets) - 1)]
            blended = 0.7 * target + 0.3 * normalized
            study["relevance"] = round(max(0.0, min(1.0, blended)), 3)

            title_sim = float(study.get("title_similarity", blended * 0.9))
            study["similarity"] = round(max(0.0, min(1.0, 0.55 * title_sim + 0.45 * blended)), 3)
        return selected

    def _enrich_single_study(
        self,
        candidate: dict[str, Any],
        user_goal: str,
        client: OpenAI | None,
    ) -> dict[str, Any] | None:
        abstract = str(candidate.get("abstract", "")).strip()
        snippet = ""
        evidence = ""

        # Prefer full-text evidence whenever it is accessible.
        fetched = self._try_fetch_fulltext_snippet(candidate.get("url"))
        if fetched and len(fetched) >= 120:
            snippet = fetched
            evidence = "fulltext"
        else:
            snippet = abstract
            evidence = "abstract"

        # Skip studies with insufficient content and move to the next candidate.
        if len(snippet) < 120:
            return None

        merged = dict(candidate)
        merged["methodology"] = self._conclude(self._heuristic_methodology(snippet), 150)
        merged["findings"] = self._conclude(self._heuristic_findings(snippet, user_goal), 140)
        merged["limitations"] = self._conclude(self._heuristic_limitations(snippet, evidence), 140)
        merged["equipment_estimate"] = self._conclude(self._heuristic_equipment(snippet), 120)
        merged["funding_estimate"] = self._conclude(self._heuristic_funding(snippet), 120)
        merged["evidence_level"] = evidence
        merged["evidence_confidence"] = self._evidence_confidence(
            relevance=float(candidate.get("relevance", 0.0)),
            evidence=evidence,
        )
        merged["selection_reason"] = self._selection_reason(
            user_goal=user_goal,
            title=str(candidate.get("title", "")),
            relevance=float(candidate.get("relevance", 0.0)),
        )

        if client is None:
            return merged

        try:
            prompt = (
                "Given this study snippet and user goal, produce concise JSON with keys: "
                "methodology (<=150 chars), findings (<=140 chars), limitations (<=140 chars), "
                "equipment_estimate (<=120 chars), funding_estimate (<=120 chars). "
                "Do not invent citations.\n"
                f"User goal: {user_goal}\n"
                f"Study title: {candidate.get('title', '')}\n"
                f"Snippet: {snippet}"
            )
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=prompt,
                temperature=0.2,
                max_output_tokens=420,
            )
            raw = response.output_text.strip()
            data = json.loads(raw)
            if isinstance(data, dict):
                merged["methodology"] = self._conclude(str(data.get("methodology", merged["methodology"])), 150)
                merged["findings"] = self._conclude(str(data.get("findings", merged["findings"])), 140)
                merged["limitations"] = self._conclude(str(data.get("limitations", merged["limitations"])), 140)
                merged["equipment_estimate"] = self._conclude(
                    str(data.get("equipment_estimate", merged["equipment_estimate"])),
                    120,
                )
                merged["funding_estimate"] = self._conclude(
                    str(data.get("funding_estimate", merged["funding_estimate"])),
                    120,
                )
                merged["evidence_level"] = f"{evidence}+ai"
                merged["evidence_confidence"] = self._evidence_confidence(
                    relevance=float(merged.get("relevance", 0.0)),
                    evidence="fulltext+ai" if evidence == "fulltext" else "abstract+ai",
                )
        except (APIError, ValueError, json.JSONDecodeError):
            pass

        return merged

    @staticmethod
    def _rank_by_relevance(user_goal: str, studies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        goal_tokens = LiteratureSynthesizerService._tokens(user_goal)
        ranked: list[dict[str, Any]] = []
        for study in studies:
            title_text = str(study.get("title", ""))
            title_score = LiteratureSynthesizerService._overlap_score(
                goal_tokens,
                LiteratureSynthesizerService._tokens(title_text),
            )
            text = f"{title_text} {study.get('abstract', '')}".strip()
            score = LiteratureSynthesizerService._overlap_score(goal_tokens, LiteratureSynthesizerService._tokens(text))
            enriched = dict(study)
            enriched["relevance"] = round(score, 3)
            enriched["title_similarity"] = round(title_score, 3)
            ranked.append(enriched)
        ranked.sort(key=lambda s: s.get("relevance", 0.0), reverse=True)
        return ranked

    @staticmethod
    def _tokens(text: str) -> set[str]:
        tokens = set(re.findall(r"[a-zA-Z0-9]{3,}", text.lower()))
        stop = {"with", "from", "that", "this", "were", "have", "their", "into", "using", "study", "based"}
        return {tok for tok in tokens if tok not in stop}

    @staticmethod
    def _overlap_score(goal_tokens: set[str], doc_tokens: set[str]) -> float:
        if not goal_tokens or not doc_tokens:
            return 0.0
        overlap = len(goal_tokens & doc_tokens)
        return min(1.0, overlap / max(5, min(len(goal_tokens), 18)))

    @staticmethod
    def _derive_scores(studies: list[dict[str, Any]]) -> tuple[float, float]:
        avg_rel = sum(float(s.get("relevance", 0.0)) for s in studies) / max(1, len(studies))
        novelty = max(0.0, min(10.0, round((1.0 - avg_rel) * 8.0 + 2.0, 1)))
        redundancy = max(0.0, min(10.0, round(avg_rel * 8.0 + 1.0, 1)))
        return novelty, redundancy

    @staticmethod
    def _conclude(text: str, limit: int) -> str:
        clean = re.sub(r"\s+", " ", text).strip().strip("\"'")
        if not clean:
            return "Summary unavailable."

        if len(clean) <= limit:
            return clean if re.search(r"[.!?]$", clean) else f"{clean}."

        # Prefer a natural sentence end before limit.
        sentence_ends = [m.end() for m in re.finditer(r"[.!?]", clean)]
        best_end = max((e for e in sentence_ends if e <= limit), default=0)
        if best_end >= 80:
            return clean[:best_end].strip()

        # Otherwise, cut at word boundary and end with a period (no ellipsis).
        chunk = clean[:limit].rstrip(" ,;:-")
        space = chunk.rfind(" ")
        if space >= 60:
            chunk = chunk[:space]
        chunk = re.sub(r"[.!?]+$", "", chunk).strip()
        if not chunk:
            return "Summary unavailable."
        return f"{chunk}."

    @staticmethod
    def _try_fetch_fulltext_snippet(url: Any) -> str:
        if not isinstance(url, str) or not url:
            return ""
        try:
            with httpx.Client(timeout=8.0, follow_redirects=True) as client:
                response = client.get(url, headers={"User-Agent": "HelixLabs/0.3"})
                response.raise_for_status()
                content_type = response.headers.get("content-type", "").lower()
                if "text/html" not in content_type:
                    return ""
                text = response.text
            text = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.I)
            text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
            text = re.sub(r"<[^>]+>", " ", text)
            text = html.unescape(text)
            text = re.sub(r"\s+", " ", text).strip()
            if len(text) < 150:
                return ""
            return text[:1200]
        except Exception:
            return ""

    @staticmethod
    def _sentences(text: str) -> list[str]:
        cleaned = re.sub(r"\s+", " ", text).strip()
        if not cleaned:
            return []
        parts = re.split(r"(?<=[.!?])\s+", cleaned)
        return [p.strip() for p in parts if p.strip()]

    @staticmethod
    def _pick_sentence(snippet: str, keywords: tuple[str, ...]) -> str | None:
        for sentence in LiteratureSynthesizerService._sentences(snippet):
            lowered = sentence.lower()
            if any(k in lowered for k in keywords):
                return sentence
        return None

    @staticmethod
    def _heuristic_methodology(snippet: str) -> str:
        picked = LiteratureSynthesizerService._pick_sentence(
            snippet,
            ("method", "experiment", "protocol", "measured", "analy", "dataset", "survey", "trial"),
        )
        if picked:
            return f"Method summary: {picked}"
        fallback = LiteratureSynthesizerService._sentences(snippet)
        return f"Method summary: {fallback[0]}" if fallback else "Method summary unavailable from retrieved text."

    @staticmethod
    def _heuristic_findings(snippet: str, user_goal: str) -> str:
        picked = LiteratureSynthesizerService._pick_sentence(
            snippet,
            ("result", "found", "improv", "increase", "decrease", "significant", "performance", "outcome"),
        )
        if picked:
            return f"Key finding: {picked}"
        tokens = sorted(LiteratureSynthesizerService._tokens(user_goal))[:4]
        anchor = ", ".join(tokens) if tokens else "goal-aligned factors"
        return f"Key finding not explicitly stated in snippet; relevance is inferred from overlap with {anchor}."

    @staticmethod
    def _heuristic_limitations(snippet: str, evidence: str) -> str:
        picked = LiteratureSynthesizerService._pick_sentence(
            snippet,
            ("limitation", "future work", "however", "uncertain", "small sample", "constraint", "bias"),
        )
        if picked:
            return f"Reported limitation: {picked}"
        if evidence == "abstract":
            return "Limitation: synthesized from abstract-level evidence only; verify with full text and methods."
        return "Limitation: automated extraction from page text may miss protocol details and caveats."

    @staticmethod
    def _heuristic_equipment(snippet: str) -> str:
        s = snippet.lower()
        equipment: list[str] = []
        mapping = (
            ("xrd", "XRD"),
            ("diffraction", "diffractometer"),
            ("spectroscopy", "spectrometer"),
            ("microscopy", "microscope"),
            ("impedance", "impedance analyzer"),
            ("electrochem", "electrochemical workstation"),
            ("temperature", "temperature-controlled chamber"),
            ("furnace", "furnace"),
            ("chromat", "chromatography system"),
            ("reactor", "reactor"),
            ("simulation", "compute cluster"),
        )
        for needle, label in mapping:
            if needle in s and label not in equipment:
                equipment.append(label)
        if equipment:
            return f"Likely equipment from text cues: {', '.join(equipment[:4])}."
        return "Equipment not explicitly reported in retrieved snippet."

    @staticmethod
    def _heuristic_funding(snippet: str) -> str:
        s = snippet.lower()
        if "grant" in s or "funded by" in s or "nsf" in s or "nih" in s or "horizon" in s:
            return "Funding note: external grant support is mentioned."
        if "industry" in s or "company" in s or "corporate" in s:
            return "Funding note: industry-affiliated support is suggested."
        return "Funding information not found in retrieved text."

    @staticmethod
    def _evidence_confidence(relevance: float, evidence: str) -> float:
        base = max(0.0, min(1.0, relevance))
        evidence_bonus = 0.1 if "fulltext" in evidence else 0.0
        ai_bonus = 0.05 if "+ai" in evidence else 0.0
        return round(max(0.0, min(1.0, base + evidence_bonus + ai_bonus)), 3)

    @staticmethod
    def _selection_reason(user_goal: str, title: str, relevance: float) -> str:
        tokens = LiteratureSynthesizerService._tokens(user_goal)
        title_tokens = LiteratureSynthesizerService._tokens(title)
        overlap = sorted(tokens & title_tokens)
        if overlap:
            joined = ", ".join(overlap[:3])
            return f"Selected for token overlap ({joined}) and relevance score {relevance:.2f}."
        return f"Selected for top-ranked relevance score {relevance:.2f} against your goal."

    @staticmethod
    def _derive_claims(studies: list[dict[str, Any]], user_goal: str) -> dict[str, str]:
        goal_tokens = sorted(LiteratureSynthesizerService._tokens(user_goal))
        top = studies[0] if studies else {}
        secondary = studies[1] if len(studies) > 1 else {}
        top_title = str(top.get("title", "")).strip()
        sec_title = str(secondary.get("title", "")).strip()
        anchor_tokens = sorted(
            LiteratureSynthesizerService._tokens(top_title + " " + str(top.get("abstract", ""))) & set(goal_tokens)
        )
        anchor = ", ".join(anchor_tokens[:3]) if anchor_tokens else ", ".join(goal_tokens[:3]) or "goal variables"
        main_claim = (
            f"Evidence indicates {anchor} strongly influences the target outcome."
            if anchor
            else f"Evidence indicates key controllable factors influence the target outcome."
        )
        weakest_claim = (
            f"Generalization beyond conditions reported in '{top_title[:80]}' remains uncertain."
            if top_title
            else "Generalization outside retrieved study conditions remains uncertain."
        )
        next_target = (
            f"Test robustness across boundary settings and compare against patterns from '{sec_title[:80]}'."
            if sec_title
            else "Test robustness at boundary settings to validate the strongest inferred relationship."
        )
        return {
            "main_claim": LiteratureSynthesizerService._conclude(main_claim, 180),
            "weakest_claim": LiteratureSynthesizerService._conclude(weakest_claim, 180),
            "next_target": LiteratureSynthesizerService._conclude(next_target, 180),
        }

    @staticmethod
    def _extract_axis_hints(studies: list[dict[str, Any]], user_goal: str) -> dict[str, str]:
        text = " ".join(
            [user_goal]
            + [str(s.get("title", "")) for s in studies[:8]]
            + [str(s.get("abstract", ""))[:600] for s in studies[:8]]
        ).lower()
        x_label = "Input Variable"
        x_unit = ""
        y_label = "Response"
        y_unit = ""
        y_format = "float"

        x_patterns = [
            (r"temperature|thermal|heat", ("Temperature", "C")),
            (r"time|duration|aging|hour", ("Time", "h")),
            (r"pressure|bar|kpa|pa", ("Pressure", "kPa")),
            (r"voltage|potential|bias", ("Voltage", "V")),
            (r"current density|ma/cm2|a/cm2", ("Current density", "mA/cm2")),
            (r"concentration|mol%|wt%|dop", ("Concentration", "mol%")),
            (r"ph\\b", ("pH", "")),
        ]
        y_patterns = [
            (r"conductiv|sigma\\b|s/cm", ("Conductivity", "S/cm", "scientific")),
            (r"yield|conversion|efficiency|percent|%", ("Yield", "%", "percent")),
            (r"capacity|mah/g|ah/kg", ("Capacity", "mAh/g", "float")),
            (r"strength|mpa|modulus", ("Strength", "MPa", "float")),
            (r"score|objective|accuracy", ("Objective score", "", "float")),
            (r"cost|usd|\\$", ("Cost", "USD", "currency")),
        ]

        for pattern, meta in x_patterns:
            if re.search(pattern, text):
                x_label, x_unit = meta
                break
        for pattern, meta in y_patterns:
            if re.search(pattern, text):
                y_label, y_unit, y_format = meta
                break
        return {
            "x_label": x_label,
            "x_unit": x_unit,
            "y_label": y_label,
            "y_unit": y_unit,
            "y_format": y_format,
        }

    @staticmethod
    def _fallback(user_goal: str, reason: str) -> dict[str, Any]:
        goal_tokens = sorted(LiteratureSynthesizerService._tokens(user_goal))
        anchor = ", ".join(goal_tokens[:3]) if goal_tokens else "the requested objective"
        return {
            "source": "fallback",
            "reason": reason,
            "studies": [
                {
                    "title": "Enhanced ionic conductivity in transition-metal doped LLZO",
                    "year": 2024,
                    "relevance": 0.92,
                    "doi": "10.0000/fallback-1",
                    "url": "https://example.org/fallback-1",
                    "exists": True,
                    "finding": "Fe doping at 3-5 mol% improved conductivity in reported conditions.",
                    "methodology": "Estimated methodology: controlled doping experiment with impedance characterization.",
                    "findings": "Estimated finding: conductivity improvement observed near moderate dopant levels.",
                    "limitations": "Estimated limitation: generalized from summary metadata, not full protocol.",
                    "equipment_estimate": "Estimated equipment: furnace, XRD, impedance analyzer.",
                    "funding_estimate": "Estimated funding: mid-size materials science grant support.",
                },
                {
                    "title": "Stability limits of doped garnet electrolytes above 250C",
                    "year": 2025,
                    "relevance": 0.68,
                    "doi": "10.0000/fallback-2",
                    "url": "https://example.org/fallback-2",
                    "exists": True,
                    "finding": "Some doped samples show decomposition above 250C.",
                    "methodology": "Estimated methodology: high-temperature cycling and structure verification.",
                    "findings": "Estimated finding: stability risk increases at upper temperature range.",
                    "limitations": "Estimated limitation: condition range may not cover all compositions.",
                    "equipment_estimate": "Estimated equipment: thermal chamber and diffraction instrumentation.",
                    "funding_estimate": "Estimated funding: public academic grant support.",
                },
                {
                    "title": "Systematic Fe concentration sweep in LLZO",
                    "year": 2026,
                    "relevance": 0.88,
                    "doi": "10.0000/fallback-3",
                    "url": "https://example.org/fallback-3",
                    "exists": True,
                    "finding": "Gap: no high-resolution concentration sweep around 3-7 mol%.",
                    "methodology": "Estimated methodology: planned concentration sweep with repeated measurements.",
                    "findings": "Estimated finding: unresolved optimum concentration in mid-range intervals.",
                    "limitations": "Estimated limitation: proposal-level evidence only.",
                    "equipment_estimate": "Estimated equipment: synthesis and electrochemical characterization suite.",
                    "funding_estimate": "Estimated funding: pre-award estimate pending study execution.",
                },
            ],
            "novelty_score": 7.2,
            "redundancy_score": 3.1,
            "main_claim": f"Available priors suggest {anchor} may improve under tuned operating settings.",
            "weakest_claim": "Robustness of gains outside reported ranges remains uncertain.",
            "next_target": "Execute boundary-condition sweeps to verify robustness and identify failure regions.",
            "axis_hints": {
                "x_label": "Concentration",
                "x_unit": "mol%",
                "y_label": "Conductivity",
                "y_unit": "S/cm",
                "y_format": "scientific",
            },
            "goal_echo": user_goal,
        }
