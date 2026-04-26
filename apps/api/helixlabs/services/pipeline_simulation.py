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
    if any(k in g for k in ("sinter", "calcine", "anneal", "firing")):
        # Typical solid-state processing window for cathode/electrolyte sintering.
        return [650.0, 700.0, 750.0, 800.0, 850.0, 900.0]
    if "cryo" in g or "low temp" in g:
        return [200.0, 250.0, 298.0]
    if "high" in g and "temp" in g:
        return [298.0, 350.0, 400.0, 450.0]
    base = [298.0, 313.0, 333.0, 353.0, 373.0]
    bump = int(fp["hash32"] % 3)
    if bump:
        base.append(393.0)
    return base


def _dwell_time_grid(user_goal: str) -> list[float]:
    g = user_goal.lower()
    if "short dwell" in g:
        return [0.5, 1.0, 2.0, 3.0]
    if "long dwell" in g:
        return [2.0, 4.0, 8.0, 12.0]
    return [1.0, 2.0, 4.0, 6.0, 8.0]


def _uses_dwell_factor(user_goal: str) -> bool:
    g = user_goal.lower()
    return any(k in g for k in ("dwell", "hold time", "soak time", "sinter"))


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
    if _uses_dwell_factor(run.user_goal):
        dwells = _dwell_time_grid(run.user_goal)
        for d in dwells:
            for t in temps:
                rows.append({"temperature_c": round(t, 2), "dwell_time_h": round(d, 2)})
        meta = {
            "fingerprint": fp,
            "n_design_points": len(rows),
            "factor_mode": "temperature_dwell",
            "fraction_anchor_mol_pct": round(float(fracs[len(fracs) // 2]), 3) if fracs else 3.0,
        }
        return rows, meta
    for f in fracs:
        for t in temps:
            rows.append({"fraction_mol_pct": f, "temperature_c": round(t, 2)})
    meta = {"fingerprint": fp, "n_design_points": len(rows), "factor_mode": "composition_temperature"}
    return rows, meta


def _sigma(
    fraction_mol_pct: float,
    temperature_c: float,
    dwell_time_h: float,
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
        + 0.03 * math.log1p(max(0.0, dwell_time_h))
        - 0.006 * max(0.0, dwell_time_h - 8.0)
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
    dwell_mode = _uses_dwell_factor(run.user_goal)
    anchor_fraction = 3.0
    if design and "fraction_mol_pct" in design[0]:
        vals = sorted({float(d.get("fraction_mol_pct", 3.0)) for d in design})
        if vals:
            anchor_fraction = vals[len(vals) // 2]
    rows: list[dict[str, Any]] = []
    for idx, point in enumerate(design):
        frac = float(point.get("fraction_mol_pct", anchor_fraction))
        temp_c = float(point["temperature_c"])
        dwell_h = float(point.get("dwell_time_h", 4.0))
        sigmas: list[float] = []
        phases: list[float] = []
        for _ in range(n_rep):
            s, ph = _sigma(frac, temp_c, dwell_h, fp, p, rng, noise)
            sigmas.append(s)
            phases.append(ph)
        row = {
            "design_index": idx,
            "temperature_c": temp_c,
            "sigma_S_cm_mean": round(sum(sigmas) / len(sigmas), 10),
            "sigma_S_cm_std": round(_pstdev(sigmas), 12) if len(sigmas) > 1 else 0.0,
            "phase_proxy_mean": round(sum(phases) / len(phases), 4),
            "n_replicates": n_rep,
        }
        if dwell_mode:
            row["dwell_time_h"] = dwell_h
        else:
            row["fraction_mol_pct"] = frac
        rows.append(row)
    return rows


def _pstdev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = sum(values) / len(values)
    var = sum((v - m) ** 2 for v in values) / (len(values) - 1)
    return math.sqrt(var)


def _clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


def _numeric_values(measurements: list[dict[str, Any]], keys: list[str]) -> tuple[str | None, list[float]]:
    for key in keys:
        vals: list[float] = []
        for row in measurements:
            try:
                val = float(row.get(key))
            except (TypeError, ValueError):
                continue
            if math.isfinite(val):
                vals.append(val)
        if vals:
            return key, vals
    return None, []


def measurement_distribution_scores(
    measurements: list[dict[str, Any]],
    *,
    response_keys: list[str] | None = None,
    risk_keys: list[str] | None = None,
    axis_keys: list[str] | None = None,
) -> dict[str, Any]:
    """Estimate EIG and risk from observed measurement spread, not fixed constants."""
    if not measurements:
        return {
            "expected_information_gain": 0.2,
            "risk_level": 0.6,
            "score_basis": {
                "n_measurements": 0,
                "reason": "no measurements available",
            },
        }

    response_key, values = _numeric_values(
        measurements,
        response_keys or ["objective_score", "sigma_S_cm_mean", "response", "y"],
    )
    if not values:
        return {
            "expected_information_gain": 0.2,
            "risk_level": 0.6,
            "score_basis": {
                "n_measurements": len(measurements),
                "reason": "no numeric response column found",
            },
        }

    values_sorted = sorted(values, reverse=True)
    best = values_sorted[0]
    second = values_sorted[1] if len(values_sorted) > 1 else best
    mean_abs = sum(abs(v) for v in values) / len(values)
    response_range = max(values) - min(values)
    response_range_ratio = response_range / (mean_abs + 1e-12)
    cv = _pstdev(values) / (mean_abs + 1e-12) if len(values) > 1 else 0.0
    margin_ratio = (best - second) / (response_range + 1e-12) if response_range > 0 else 0.0
    ambiguity = 1.0 - _clamp(margin_ratio)

    best_row = max(measurements, key=lambda row: _safe_float(row.get(response_key), float("-inf")))
    edge_best = 0.0
    for axis_key in axis_keys or ["x1", "u1", "fraction_mol_pct", "dwell_time_h", "temperature_c"]:
        axis_vals = [_safe_float(row.get(axis_key), math.nan) for row in measurements]
        axis_vals = [v for v in axis_vals if math.isfinite(v)]
        if len(axis_vals) < 3:
            continue
        best_axis = _safe_float(best_row.get(axis_key), math.nan)
        if not math.isfinite(best_axis):
            continue
        lo, hi = min(axis_vals), max(axis_vals)
        span = hi - lo
        if span <= 1e-12:
            continue
        position = (best_axis - lo) / span
        if position <= 0.12 or position >= 0.88:
            edge_best = 1.0
            break

    risk_key, risk_values = _numeric_values(
        measurements,
        risk_keys or ["phase_proxy_mean", "stability_pass", "risk_score"],
    )
    risk_from_metric = None
    if risk_key == "phase_proxy_mean" and risk_values:
        below_threshold = sum(1 for v in risk_values if v < 0.82) / len(risk_values)
        worst_deficit = max(0.0, 0.82 - min(risk_values)) / 0.82
        risk_from_metric = _clamp(0.12 + 0.58 * below_threshold + 0.3 * worst_deficit)
    elif risk_key == "stability_pass" and risk_values:
        failures = sum(1 for v in risk_values if v < 0.5) / len(risk_values)
        risk_from_metric = _clamp(0.1 + 0.75 * failures)
    elif risk_key == "risk_score" and risk_values:
        risk_from_metric = _clamp(sum(risk_values) / len(risk_values))

    eig = _clamp(0.12 + 0.34 * min(1.0, response_range_ratio) + 0.24 * min(1.0, cv) + 0.22 * ambiguity)
    if risk_from_metric is None:
        risk = _clamp(0.12 + 0.3 * min(1.0, cv) + 0.24 * edge_best + 0.18 * ambiguity)
    else:
        risk = _clamp(0.7 * risk_from_metric + 0.18 * edge_best + 0.12 * min(1.0, cv))

    return {
        "expected_information_gain": round(eig, 4),
        "risk_level": round(risk, 4),
        "score_basis": {
            "n_measurements": len(measurements),
            "response_key": response_key,
            "response_min": round(min(values), 6),
            "response_max": round(max(values), 6),
            "response_cv": round(cv, 6),
            "top_margin_ratio": round(margin_ratio, 6),
            "risk_key": risk_key,
            "edge_best": bool(edge_best),
            "method": "measurement_distribution",
        },
    }


def _safe_float(value: Any, default: float) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


def aggregate_series(measurements: list[dict[str, Any]]) -> dict[str, Any]:
    """Series for plotting built from a concrete measured slice to match visible observations."""
    if not measurements:
        return {"label": "No measurements", "temperature_c": [], "sigma_S_cm": []}

    if any("dwell_time_h" in m for m in measurements):
        dwell_vals = sorted({float(m.get("dwell_time_h", 0.0)) for m in measurements})
        target_dwell = dwell_vals[len(dwell_vals) // 2]
        filtered = [m for m in measurements if abs(float(m.get("dwell_time_h", 0.0)) - target_dwell) < 1e-9]
        filtered.sort(key=lambda m: float(m["temperature_c"]))
        return {
            "label": f"Measured σ (S/cm) vs temperature at dwell={target_dwell:g} h",
            "temperature_c": [round(float(m["temperature_c"]), 2) for m in filtered],
            "sigma_S_cm": [round(float(m["sigma_S_cm_mean"]), 10) for m in filtered],
            "slice_factor": "dwell_time_h",
            "slice_value": target_dwell,
        }

    if any("fraction_mol_pct" in m for m in measurements):
        frac_vals = sorted({float(m.get("fraction_mol_pct", 0.0)) for m in measurements})
        target_frac = frac_vals[len(frac_vals) // 2]
        filtered = [m for m in measurements if abs(float(m.get("fraction_mol_pct", 0.0)) - target_frac) < 1e-9]
        filtered.sort(key=lambda m: float(m["temperature_c"]))
        return {
            "label": f"Measured σ (S/cm) vs temperature at composition={target_frac:g} mol%",
            "temperature_c": [round(float(m["temperature_c"]), 2) for m in filtered],
            "sigma_S_cm": [round(float(m["sigma_S_cm_mean"]), 10) for m in filtered],
            "slice_factor": "fraction_mol_pct",
            "slice_value": target_frac,
        }

    by_t: dict[float, list[float]] = {}
    for m in measurements:
        t = float(m["temperature_c"])
        by_t.setdefault(t, []).append(float(m["sigma_S_cm_mean"]))
    temps = sorted(by_t.keys())
    sigmas = [sum(by_t[t]) / len(by_t[t]) for t in temps]
    return {
        "label": "Measured σ (S/cm) vs temperature",
        "temperature_c": [round(t, 2) for t in temps],
        "sigma_S_cm": [round(s, 10) for s in sigmas],
    }


def interpret_from_measurements(measurements: list[dict[str, Any]]) -> dict[str, Any]:
    if not measurements:
        return {"inference": "No measurements available.", "uncertainty": "n/a"}
    best = max(measurements, key=lambda m: float(m["sigma_S_cm_mean"]))
    worst_phase = min(measurements, key=lambda m: float(m["phase_proxy_mean"]))
    primary_axis_key = "fraction_mol_pct" if "fraction_mol_pct" in best else "dwell_time_h" if "dwell_time_h" in best else "design_index"
    primary_axis_value = best.get(primary_axis_key)
    return {
        "best_condition": {
            primary_axis_key: primary_axis_value,
            "temperature_c": best["temperature_c"],
            "sigma_S_cm_mean": best["sigma_S_cm_mean"],
        },
        "stability_risk_condition": {
            primary_axis_key: worst_phase.get(primary_axis_key),
            "temperature_c": worst_phase["temperature_c"],
            "phase_proxy_mean": worst_phase["phase_proxy_mean"],
        },
        "inference": (
            f"Highest modeled conductivity at {primary_axis_key}={primary_axis_value} and {best['temperature_c']} °C "
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
            "score_basis": {"n_measurements": 0, "reason": "no measurements available"},
        }
    best = max(measurements, key=lambda m: float(m["sigma_S_cm_mean"]))
    if "fraction_mol_pct" in best:
        primary_axis = "fraction_mol_pct"
        bf = float(best["fraction_mol_pct"])
        span = 0.6 + fp["mean_similarity"] * 0.4
        lo, hi = max(0.05, bf - span), bf + span
        axis_note = f"Refine composition near {bf:.2f} mol% (suggested window {lo:.2f}–{hi:.2f} mol%)"
    else:
        primary_axis = "dwell_time_h"
        bf = float(best.get("dwell_time_h", 4.0))
        span = 1.0 + fp["mean_similarity"] * 1.5
        lo, hi = max(0.5, bf - span), bf + span
        axis_note = f"Refine dwell time near {bf:.2f} h (suggested window {lo:.2f}–{hi:.2f} h)"
    scores = measurement_distribution_scores(
        measurements,
        response_keys=["sigma_S_cm_mean"],
        risk_keys=["phase_proxy_mean"],
        axis_keys=[primary_axis, "temperature_c"],
    )
    return {
        "recommendation": f"{axis_note} with extra temperature points around {best['temperature_c']} °C.",
        "primary_axis": primary_axis,
        "expected_information_gain": scores["expected_information_gain"],
        "risk_level": scores["risk_level"],
        "score_basis": scores["score_basis"],
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
    if design:
        axis_keys = [k for k in design[0].keys() if k not in {"design_index"}]
    else:
        axis_keys = ["temperature_c"]
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
            "axes": axis_keys,
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
    has_fraction = any("fraction_mol_pct" in m for m in measurements)
    has_dwell = any("dwell_time_h" in m for m in measurements)
    mapped = {
        "temperature_c": "temperature",
        "sigma_S_cm_mean": "conductivity",
        "phase_proxy_mean": "phase_quality_proxy",
    }
    if has_fraction:
        mapped["fraction_mol_pct"] = "composition_fraction"
    if has_dwell:
        mapped["dwell_time_h"] = "dwell_time"
    return {
        "validation_status": "repaired" if measurements else "skipped",
        "mapped_columns": mapped,
        "validated_records": len(measurements),
    }


def report_payload(run: RunRecord, measurements: list[dict[str, Any]], interp: dict[str, Any]) -> dict[str, Any]:
    lit = run.pipeline.intake.literature or {}
    dois = [str(s.get("doi", "")) for s in list(lit.get("studies") or []) if s.get("doi")][:6]
    return {
        "title": "HelixLabs experiment report (literature-conditioned simulation)",
        "summary": interp.get("inference", ""),
        "scope_note": (
            "Evidence-conditioned simulation for planning support; not a protocol-faithful replication "
            "of any individual source study."
        ),
        "run_id": run.run_id,
        "source_studies": dois,
        "n_measurements": len(measurements),
    }
