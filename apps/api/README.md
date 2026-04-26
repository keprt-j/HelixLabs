# API Scaffold

This folder is the Python backend entrypoint for HelixLabs.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

## Current endpoints

- `GET /api/health`
- `POST /api/runs`
- `GET /api/runs/{run_id}`
- `POST /api/runs/{run_id}/advance`
- `GET /api/runs/{run_id}/report`
- `GET /api/runs/{run_id}/events`

## Current architecture

- `helixlabs/domain/models.py`: canonical Pydantic run models and states.
- `helixlabs/repos/json_run_repository.py`: JSON persistence under `data/runtime/`.
- `helixlabs/services/stage_service.py`: deterministic stage payload generation.
- `helixlabs/services/literature_retriever.py`: DOI-backed study retrieval (Crossref with OpenAlex fallback).
- `helixlabs/services/literature_synthesizer.py`: relevance ranking + optional OpenAI claim synthesis.
- `helixlabs/services/orchestrator.py`: run lifecycle transitions and persistence.
- `helixlabs/api/routes.py`: FastAPI endpoints over orchestrator.

This now provides a functional MVP workflow engine that can be wired directly to the dashboard.

## Environment

Set `OPENAI_API_KEY` in your local `.env` to enable model-backed literature synthesis.
If unavailable, the backend automatically falls back to deterministic seed synthesis.
Internet access is required for live literature retrieval.
