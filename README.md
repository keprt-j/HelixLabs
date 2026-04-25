# HelixLabs

**HelixLabs is a cloud-lab operating system for autonomous science.**

It compiles scientific intent into evidence-aware, non-redundant, scheduled, executable, validated, recoverable experiments, then recommends the next highest-value experiment.

---

## Canonical Demo

Input:

> Find a low-cost cobalt-free cathode material and test whether Mn doping improves conductivity without hurting stability.

Expected HelixLabs behavior:

1. Parse the goal into structured scientific intent.
2. Search live literature with cached fallback.
3. Detect prior low-Mn tests.
4. Detect a negative high-Mn result.
5. Build a claim graph.
6. Compile a narrowed 12%, 14%, 16% Mn experiment.
7. Validate feasibility, controls, resources, and schema.
8. Score novelty, redundancy, and experiment value.
9. Generate a protocol.
10. Schedule simulated lab resources.
11. Pause for human approval.
12. Execute a simulated lab run.
13. Recover from a simulated timeout.
14. Detect result schema drift.
15. Repair output data.
16. Interpret the result.
17. Recommend a boundary screen at 14.5%, 15.0%, and 15.5%.
18. Generate a provenance report.
19. Update experiment memory.

---

## Architecture Summary

```text
Input:
Research goal

Evidence layer:
Live literature search
Prior experiment search
Evidence extraction
Experiment matching
Negative-results memory

Reasoning layer:
Scientific intent parser
Claim graph builder
Uncertainty identification

Compilation layer:
Experiment IR compiler
Feasibility validator
Novelty/redundancy/value scorer
Protocol generator

Operating layer:
Resource scheduler
Human approval gate
Execution adapters
Simulated/API-backed lab runner
Failure recovery engine

Data layer:
Expected schemas
Data stent
Repair engine
Result interpreter

Iteration layer:
Next experiment planner
Provenance report
Experiment memory update

Output:
A non-redundant, evidence-aware, scheduled, validated, recoverable experiment and the next highest-value experiment to run.
```

---

## Recommended Stack

Backend:

- Python 3.11+
- FastAPI
- Pydantic v2
- SQLite or local JSON persistence
- pytest

Frontend:

- React or Next.js
- TypeScript
- Tailwind CSS if available

Data:

- pandas
- Pydantic validation
- Optional `frictionless`

Live literature search:

- Semantic Scholar, Crossref, arXiv, or PubMed
- Cached fallback required

---

## Development Setup

These commands are intentionally generic. Codex should update them after implementation.

### Backend

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

If using Windows PowerShell:

```powershell
cd apps/api
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd apps/web
npm install
npm run dev
```

---

## Environment Variables

Copy `.env.example` to `.env`.

Live search should work without keys if using public endpoints, but the demo must fall back to cached data if any live search fails.

---

## Important Project Files

- `AGENTS.md` — instructions for Codex and coding agents
- `PLAN.md` — full product architecture
- `API_CONTRACTS.md` — schemas and endpoint contracts
- `IMPLEMENTATION_CHECKLIST.md` — step-by-step build tracker
- `CODEX_PROMPTS.md` — recommended prompts for Codex
- `.env.example` — environment variable template

---

## Implementation Priorities

Build in this order:

1. Core models and state machine.
2. Canonical demo state advancement.
3. Literature search with fallback.
4. Prior-work and negative-results matching.
5. Experiment IR compilation.
6. Feasibility and value scoring.
7. Protocol generation.
8. Scheduling.
9. Approval gate.
10. Simulated execution.
11. Failure recovery.
12. Data stent validation and repair.
13. Result interpretation.
14. Next experiment planning.
15. Provenance report.
16. Frontend dashboard polish.

---

## Validation Checklist

Before demo:

- Backend starts.
- Frontend starts.
- Canonical demo works end-to-end.
- Live search failure triggers fallback.
- Prior work is detected.
- Negative result is detected.
- Experiment IR narrows to 12%, 14%, 16%.
- Simulated failure occurs and is recovered.
- Schema drift is detected and repaired.
- Next experiment is 14.5%, 15.0%, 15.5%.
- Provenance report is generated.
