# HelixLabs

## Team

Team name: HelixLabs

Project members:
- Jaxon Bentivegna
- Julia Dacayanan
- Aryan Ghariwala
- Joshua John
- Siddhartha Sureban

## Track

Autonomous Labs

## What We Built

HelixLabs is a full-stack autonomous science workflow dashboard. It turns a research goal into an evidence-aware experiment plan, checks prior work and negative results, builds a claim graph, compiles an Experiment IR, validates feasibility, scores novelty/value, generates a protocol, schedules lab resources, pauses for human approval, simulates execution, repairs result schema drift, interprets results, recommends the next experiment, and records provenance.

The app includes:
- FastAPI backend with persisted run state and provenance events
- React/Vite dashboard frontend
- Live literature search with cached fallback behavior
- LLM-assisted scientific intent, claim, and JSON summary generation
- Prior-work and negative-results matching
- Experiment compiler, feasibility validator, value scorer, protocol generator, scheduler, execution simulator, recovery planner, data validation/repair, interpretation, recommendation, and report artifacts
- Collapsible JSON inspectors with generated summaries for pipeline and artifact payloads

## Datasets and APIs Used

- Crossref public API for live literature retrieval
- OpenAI API for structured extraction, claim polishing, and artifact/pipeline summaries
- Local seeded fallback literature and runtime data for reliable demos when live literature retrieval is unavailable
- Local JSON persistence in `data/runtime/` for run state, artifacts, provenance, and evidence caches

## How To Run It

### Prerequisites

- Node.js 18+
- Python 3.11+
- An OpenAI API key in `.env`

Example `.env` at the repo root:

```bash
OPENAI_API_KEY=your_key_here
HELIXLABS_OPENAI_MODEL=gpt-4.1-mini
```

### Install Frontend Dependencies

```bash
npm install
```

### Install Backend Dependencies

Windows PowerShell:

```powershell
cd apps/api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd ../..
```

macOS/Linux:

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd ../..
```

### Start The Backend

From the repo root:

```bash
npm run dev:api
```

Backend health check:

```bash
curl http://127.0.0.1:8000/api/health
```

### Start The Frontend

In a second terminal, from the repo root:

```bash
npm run dev
```

Open:

```text
http://localhost:5173/
```

## Tests

Backend tests:

```bash
PYTHONPATH=apps/api python -m unittest discover apps/api/tests
```

Frontend tests:

```bash
npm run test:frontend
```

Production build:

```bash
npm run build
```
