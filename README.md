# HelixLabs

HelixLabs is evolving from a UI prototype into a full-stack experiment workflow platform.

## What changed

- Frontend pipeline sections were merged into four logical stages:
  - Intake & Prior Work
  - Planning Pipeline
  - Runtime Pipeline
  - Outcomes & Provenance
- Unused UI-kit surface area and related dependencies were removed.
- A Python backend scaffold now exists under `apps/api`.
- A shared contract layer now exists under `packages/contracts`.
- Runtime storage space is prepared in `data/runtime/`.

## Repo layout

```text
apps/
  api/                  FastAPI backend scaffold
data/
  runtime/              Runtime snapshots and state persistence
packages/
  contracts/            Shared JSON schema contracts
src/
  app/                  React dashboard UI
```

## Frontend setup

```bash
npm install
npm run dev
```

## Backend setup

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Health check:

- `GET http://127.0.0.1:8000/api/health`

Prompt library for demos/reviewers:

- See `PROMPT_LIBRARY.md`
  