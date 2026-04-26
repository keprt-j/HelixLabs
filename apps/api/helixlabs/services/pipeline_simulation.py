"""
Literature-grounded experiment simulation.

Produces measurement tables and downstream artifacts from (a) retrieved studies and
(b) a deterministic RNG seeded per run. Exposes knobs for future variability: replicates,
noise policy, and optional env overrides.
"""

from __future__ import annotations

import hashlib
import math
import os
import random
import re
from typing import Any

from helixlabs.domain.models import RunRecord


def simulation_seed(run_id: str, user_goal: str) -> int:
    """Stable per-run seed (reproducible replays). Override with HELIX_SIM_SEED for debugging."""
    env = os.getenv("HELIX_SIM_SEED", "").strip()
    if env.isdigit():
        return int(env) % (2**31)
    raw = hashlib.sha256(f"{run_id}|{user_goal}".encode()).digest()
    return int.from_bytes(raw[:4], "big") % (2**31)


def _sim_overrides(run: RunRecord) -> dict[str, Any]:
    v = run.artifacts.get("simulation_overrides")
    if isinstance(v, dict):
        return v
    return {}


def simulation_seed_for_run(run: RunRecord) -> int:
    overrides = _sim_overrides(run)
    candidate = overrides.get("seed")
    if isinstance(candidate, int):
        return int(candidate) % (2**31)
    if isinstance(candidate, str) and candidate.strip().isdigit():
        return int(candidate.strip()) % (2**31)
    return simulation_seed(run.run_id, run.user_goal)


def noise_scale_default() -> float:
    v = os.getenv("HELIX_SIM_NOISE", "0.06").strip()
    try:
        return max(0.0, min(0.25, float(v)))
    except ValueError:
        return 0.06


def noise_scale_for_run(run: RunRecord) -> float:
    overrides = _sim_overrides(run)
    candidate = overrides.get("noise_scale_relative")
    if isinstance(candidate, (int, float)):
        return max(0.0, min(0.25, float(candidate)))
    if isinstance(candidate, str):
        try:
            return max(0.0, min(0.25, float(candidate.strip())))
        except ValueError:
            return noise_scale_default()
    return noise_scale_default()


def n_replicates_default() -> int:
    v = os.getenv("HELIX_SIM_N_REPLICATES", "1").strip()
    try:
        return max(1, min(20, int(v)))
    except ValueError:
        return 1


def n_replicates_for_run(run: RunRecord) -> int:
    overrides = _sim_overrides(run)
    candidate = overrides.get("n_replicates")
    if isinstance(candidate, int):
        return max(1, min(20, int(candidate)))
    if isinstance(candidate, str):
        try:
            return max(1, min(20, int(candidate.strip())))
        except ValueError:
            return n_replicates_default()
    return n_replicates_default()


def design_density_for_run(run: RunRecord) -> str:
    overrides = _sim_overrides(run)
    v = str(overrides.get("design_density", "medium")).strip().lower()
    if v in {"coarse", "medium", "fine"}:
        return v
    return "medium"


def literature_fingerprint(studies: list[dict[str, Any]], user_goal: str) -> dict[str, Any]:
    """Compress retrieved studies into stable numeric features for the simulator."""
    if not studies:
        blob = user_goal.encode()
        h = int.from_bytes(hashlib.sha256(blob).digest()[:4], "big")
        return {
            "n_studies": 0,
            "mean_relevance": 0.45,
            "mean_similarity": 0.45,
            "hash32": int(h % (2**32)),
            "top_tokens": [],
            "study_refs": [],
        }
    rels = [float(s.get("relevance", 0.0)) for s in studies]
    sims = [float(s.get("similarity", s.get("relevance", 0.0))) for s in studies]
    texts: list[str] = []
    refs: list[dict[str, Any]] = []
    for s in studies[:8]:
        doi = str(s.get("doi", ""))
        title = str(s.get("title", ""))[:120]
        texts.append(f"{doi}|{title}|{str(s.get('abstract', ''))[:200]}")
        refs.append({"doi": doi, "title": title, "relevance": float(s.get("relevance", 0.0))})
    blob = "\n".join(texts).encode() + user_goal.encode()
    h = int.from_bytes(hashlib.sha256(blob).digest()[:4], "big")
    goal_tokens = _tokens(user_goal)
    top_tokens: list[str] = []
    for s in studies[:3]:
        top_tokens.extend(list(_tokens(str(s.get("title", ""))))[:6])
    top_tokens = list(dict.fromkeys([t for t in top_tokens if t in goal_tokens or len(t) > 4]))[:12]
    return {
        "n_studies": len(studies),
        "mean_relevance": sum(rels) / len(rels),
        "mean_similarity": sum(sims) / len(sims),
        "hash32": int(h % (2**32)),
        "top_tokens": top_tokens,
        "study_refs": refs,
    }


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z0-9]{4,}", text.lower()))


def build_simulation_config(run: RunRecord) -> dict[str, Any]:
    """Serialized config + hooks for future variability (replicates, sweeps, external simulators)."""
    lit = run.pipeline.intake.literature or {}
    studies = list(lit.get("studies") or [])
    fp = literature_fingerprint(studies, run.user_goal)
    seed = simulation_seed_for_run(run)
    return {
        "version": 1,
        "seed": seed,
        "noise_scale_relative": noise_scale_for_run(run),
        "n_replicates": n_replicates_for_run(run),
        "design_density": design_density_for_run(run),
        "literature_signal_strength": round(fp["mean_relevance"], 4),
        "n_source_studies": fp["n_studies"],
        "study_refs": fp["study_refs"],
        "extensions": {
            "description": "Increase HELIX_SIM_N_REPLICATES for Monte Carlo; set HELIX_SIM_NOISE for relative log-normal noise.",
            "reserved": ["external_backend", "surrogate_model_id", "calibration_run_id"],
        },
    }


def _model_params(fp: dict[str, Any], rng: random.Random) -> dict[str, float]:
    h = int(fp["hash32"])
    # Peak location and width depend on literature fingerprint (different runs differ).
    peak_frac = 1.5 + (h % 5000) / 1250.0  # ~1.5–5.5 mol%
    width = 1.1 + rng.uniform(0.15, 0.55)
    base_log_sigma = -4.35 + (fp["mean_relevance"] * 0.55) + ((h >> 8) % 255) / 2000.0
    temp_coef = 0.0018 + fp["mean_relevance"] * 0.0022
    curvature = 0.035 + rng.uniform(0, 0.02)
    return {
        "peak_frac": peak_frac,
        "width": width,
        "base_log_sigma": base_log_sigma,
        "temp_coef": temp_coef,
        "curvature": curvature,
    }


def _fraction_grid(n_levels: int, fp: dict[str, Any], rng: random.Random) -> list[float]:
    h = fp["hash32"]
    lo = 0.2 + (h % 200) / 500.0
    hi = 6.0 + (h >> 3) % 400 / 100.0
    if fp["mean_relevance"] > 0.75:
        hi = min(hi, 5.5)
    step = (hi - lo) / max(1, n_levels - 1)
    return [round(lo + i * step, 3) for i in range(n_levels)]


def _temperature_grid(user_goal: str, fp: dict[str, Any]) -> list[float]:
    g = user_goal.lower()
    if "cryo" in g or "low temp" in g:
        return [200.0, 250.0, 298.0]
    if "high" in g and "temp" in g:
        return [298.0, 350.0, 400.0, 450.0]
    base = [298.0, 313.0, 333.0, 353.0, 373.0]
    bump = int(fp["hash32"] % 3)
    if bump:
        base.append(393.0)
    return base


def design_experiment_matrix(run: RunRecord) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    lit = run.pipeline.intake.literature or {}
    studies = list(lit.get("studies") or [])
    fp = literature_fingerprint(studies, run.user_goal)
    rng = random.Random(simulation_seed_for_run(run))
    n_levels = 5 + int(fp["mean_relevance"] * 4)  # 5–8 conditions along composition
    density = design_density_for_run(run)
    if density == "coarse":
        n_levels = max(4, n_levels - 1)
    elif density == "fine":
        n_levels = min(10, n_levels + 2)
    fracs = _fraction_grid(n_levels, fp, rng)
    temps = _temperature_grid(run.user_goal, fp)
    rows: list[dict[str, Any]] = []
    for f in fracs:
        for t in temps:
            rows.append({"fraction_mol_pct": f, "temperature_c": round(t, 2)})
    meta = {"fingerprint": fp, "n_design_points": len(rows)}
    return rows, meta


def _sigma(
    fraction_mol_pct: float,
    temperature_c: float,
    fp: dict[str, Any],
    p: dict[str, float],
    rng: random.Random,
    noise_scale: float,
) -> tuple[float, float]:
    x = (fraction_mol_pct - p["peak_frac"]) / max(0.35, p["width"])
    log_s = (
        p["base_log_sigma"]
        - p["curvature"] * x * x
        + p["temp_coef"] * (temperature_c - 298.0) / 75.0
        + fp["mean_relevance"] * 0.12
    )
    noise = rng.gauss(0.0, noise_scale)
    sigma = math.exp(log_s + noise)
    # Phase proxy: worse away from peak (simple stand-in for stability)
    phase_proxy = max(0.0, min(1.0, 0.92 - 0.06 * abs(x) + rng.uniform(-0.02, 0.02)))
    return max(1e-9, sigma), phase_proxy


def run_measurements(run: RunRecord, design: list[dict[str, Any]], fp: dict[str, Any]) -> list[dict[str, Any]]:
    seed = simulation_seed_for_run(run)
    rng = random.Random(seed)
    noise = noise_scale_for_run(run)
    n_rep = n_replicates_for_run(run)
    p = _model_params(fp, rng)
    rows: list[dict[str, Any]] = []
    for idx, point in enumerate(design):
        frac = float(point["fraction_mol_pct"])
        temp_c = float(point["temperature_c"])
        sigmas: list[float] = []
        phases: list[float] = []
        for _ in range(n_rep):
            s, ph = _sigma(frac, temp_c, fp, p, rng, noise)
            sigmas.append(s)
            phases.append(ph)
        rows.append(
            {
                "design_index": idx,
                "fraction_mol_pct": frac,
                "temperature_c": temp_c,
                "sigma_S_cm_mean": round(sum(sigmas) / len(sigmas), 10),
                "sigma_S_cm_std": round(_pstdev(sigmas), 12) if len(sigmas) > 1 else 0.0,
                "phase_proxy_mean": round(sum(phases) / len(phases), 4),
                "n_replicates": n_rep,
            }
        )
    return rows


def _pstdev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = sum(values) / len(values)
    var = sum((v - m) ** 2 for v in values) / (len(values) - 1)
    return math.sqrt(var)


def aggregate_series(measurements: list[dict[str, Any]]) -> dict[str, Any]:
    """Series for plotting: sigma vs temperature (mean over fraction bands)."""
    by_t: dict[float, list[float]] = {}
    for m in measurements:
        t = float(m["temperature_c"])
        by_t.setdefault(t, []).append(float(m["sigma_S_cm_mean"]))
    temps = sorted(by_t.keys())
    sigmas = [sum(by_t[t]) / len(by_t[t]) for t in temps]
    return {
        "label": "Mean σ (S/cm) vs temperature (averaged over composition grid)",
        "temperature_c": [round(t, 2) for t in temps],
        "sigma_S_cm": [round(s, 10) for s in sigmas],
    }


def interpret_from_measurements(measurements: list[dict[str, Any]]) -> dict[str, Any]:
    if not measurements:
        return {"inference": "No measurements available.", "uncertainty": "n/a"}
    best = max(measurements, key=lambda m: float(m["sigma_S_cm_mean"]))
    worst_phase = min(measurements, key=lambda m: float(m["phase_proxy_mean"]))
    return {
        "best_condition": {
            "fraction_mol_pct": best["fraction_mol_pct"],
            "temperature_c": best["temperature_c"],
            "sigma_S_cm_mean": best["sigma_S_cm_mean"],
        },
        "stability_risk_condition": {
            "fraction_mol_pct": worst_phase["fraction_mol_pct"],
            "temperature_c": worst_phase["temperature_c"],
            "phase_proxy_mean": worst_phase["phase_proxy_mean"],
        },
        "inference": (
            f"Highest modeled conductivity at {best['fraction_mol_pct']} mol% and {best['temperature_c']} °C "
            f"(σ ≈ {best['sigma_S_cm_mean']} S/cm), derived from the literature-conditioned surrogate."
        ),
        "uncertainty": (
            "Surrogate is not a physical model; uncertainty is epistemic (limited to retrieved abstracts and noise policy)."
        ),
    }


def recommend_next_from_measurements(measurements: list[dict[str, Any]], fp: dict[str, Any]) -> dict[str, Any]:
    if not measurements:
        return {
            "recommendation": "Acquire richer literature or broaden the goal to unlock a design grid.",
            "expected_information_gain": 0.2,
            "risk_level": 0.6,
        }
    best = max(measurements, key=lambda m: float(m["sigma_S_cm_mean"]))
    bf = float(best["fraction_mol_pct"])
    span = 0.6 + fp["mean_similarity"] * 0.4
    lo, hi = max(0.05, bf - span), bf + span
    eigs = min(0.98, 0.55 + fp["mean_relevance"] * 0.35)
    risk = max(0.08, 0.45 - fp["mean_relevance"] * 0.25)
    return {
        "recommendation": (
            f"Refine composition near {bf:.2f} mol% (suggested window {lo:.2f}–{hi:.2f} mol%) "
            f"with extra temperature points around {best['temperature_c']} °C."
        ),
        "expected_information_gain": round(eigs, 3),
        "risk_level": round(risk, 3),
        "anchor_study_dois": [r.get("doi") for r in fp.get("study_refs", []) if r.get("doi")][:3],
    }


def feasibility_from_literature_and_design(
    run: RunRecord, design: list[dict[str, Any]], fp: dict[str, Any]
) -> dict[str, Any]:
    issues: list[str] = []
    max_t = max((float(p["temperature_c"]) for p in design), default=298.0)
    titles = " ".join(str(s.get("title", "")).lower() for s in (run.pipeline.intake.literature or {}).get("studies") or [])
    if max_t > 380 and ("stability" in titles or "decom" in titles or "limit" in titles):
        issues.append("High-temperature cells overlap with literature stability concerns.")
    if fp["mean_relevance"] < 0.35:
        issues.append("Low average literature relevance; measurements are weakly anchored to evidence.")
    if fp["n_studies"] < 2:
        issues.append("Few qualifying studies; widen retrieval or relax text thresholds.")
    status = "passed" if not issues else "passed_with_warnings"
    return {"validation_status": status, "issues": issues}


def schedule_from_design(run: RunRecord, design: list[dict[str, Any]], fp: dict[str, Any]) -> dict[str, Any]:
    n = len(design)
    hours_per = 0.22 + (1.0 - fp["mean_relevance"]) * 0.08
    total = round(3.5 + n * hours_per, 1)
    util = min(92, round(48 + fp["mean_relevance"] * 38))
    idle = max(0.5, round(total * (1.0 - util / 130.0), 1))
    return {
        "schedule_id": f"SCH-{run.run_id}",
        "total_duration_hours": total,
        "resource_utilization_pct": util,
        "idle_time_hours": idle,
        "design_points": n,
        "hours_per_design_point": round(hours_per, 3),
    }


def value_scores_from_context(
    fp: dict[str, Any], measurements: list[dict[str, Any]], prior_work: dict[str, Any]
) -> dict[str, Any]:
    spread = 0.0
    if len(measurements) > 1:
        vals = [float(m["sigma_S_cm_mean"]) for m in measurements]
        spread = (_pstdev(vals) or 0.0) / (sum(vals) / len(vals) + 1e-12)
    eigs = min(0.98, 0.42 + fp["mean_relevance"] * 0.28 + min(0.22, spread * 2.0))
    overall = min(0.98, 0.4 + fp["mean_relevance"] * 0.35 + eigs * 0.2)
    return {
        "redundancy_score": prior_work.get("redundancy_score", 3.0),
        "novelty_score": prior_work.get("novelty_score", 7.0),
        "expected_information_gain": round(eigs, 4),
        "overall_experiment_value": round(overall, 4),
        "sigma_spread_coefficient_of_variation": round(spread, 6),
    }


def protocol_from_design(run: RunRecord, design: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "protocol_id": f"P-{run.run_id}",
        "steps": [
            "prepare_powders",
            "ball_mill",
            "sinter_schedule",
            "impedance_sweep",
            "structure_check",
            "export_measurement_bundle",
        ],
        "design_space": {
            "n_points": len(design),
            "axes": ["fraction_mol_pct", "temperature_c"],
        },
    }


def execution_payload(
    run: RunRecord,
    design: list[dict[str, Any]],
    measurements: list[dict[str, Any]],
    fp: dict[str, Any],
) -> dict[str, Any]:
    cfg = build_simulation_config(run)
    series = aggregate_series(measurements)
    low_phase = [m for m in measurements if float(m["phase_proxy_mean"]) < 0.82]
    had_issue = bool(low_phase)
    return {
        "status": "completed_with_recovery" if had_issue else "completed",
        "current_step": len(measurements),
        "total_steps": len(measurements),
        "simulation_config": cfg,
        "measurements": measurements,
        "series_for_charts": [series],
        "recovery_hint": (
            "Low phase_proxy on some cells; surrogate suggests rework or narrowed composition window."
            if had_issue
            else None
        ),
        "literature_fingerprint": {"mean_relevance": fp["mean_relevance"], "n_studies": fp["n_studies"]},
    }


def recovery_payload(measurements: list[dict[str, Any]]) -> dict[str, Any]:
    low = [m for m in measurements if float(m["phase_proxy_mean"]) < 0.82]
    if not low:
        return {"selected_recovery": "none", "status": "not_required", "notes": "No surrogate stability flags."}
    return {
        "selected_recovery": "narrow_composition_window",
        "status": "applied",
        "affected_design_indices": [m["design_index"] for m in low[:8]],
        "notes": "Surrogate phase_proxy dipped below threshold on edge compositions.",
    }


def validation_payload(measurements: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "validation_status": "repaired" if measurements else "skipped",
        "mapped_columns": {
            "fraction_mol_pct": "composition_fraction",
            "temperature_c": "temperature",
            "sigma_S_cm_mean": "conductivity",
            "phase_proxy_mean": "phase_quality_proxy",
        },
        "validated_records": len(measurements),
    }


def report_payload(run: RunRecord, measurements: list[dict[str, Any]], interp: dict[str, Any]) -> dict[str, Any]:
    lit = run.pipeline.intake.literature or {}
    dois = [str(s.get("doi", "")) for s in list(lit.get("studies") or []) if s.get("doi")][:6]
    return {
        "title": "HelixLabs experiment report (literature-conditioned simulation)",
        "summary": interp.get("inference", ""),
        "run_id": run.run_id,
        "source_studies": dois,
        "n_measurements": len(measurements),
    }
