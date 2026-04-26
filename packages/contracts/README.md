# Data Contracts

This package hosts shared contracts between frontend and backend.

- `run.schema.json`: canonical JSON Schema for run payloads.
- `experiment-ir.schema.json`: universal experiment intermediate representation contract.

## Intent

1. Python backend validates inbound/outbound payloads against this schema.
2. Frontend derives strong types from the same schema.
3. Runtime snapshots can be persisted in `data/runtime/` as contract-compliant JSON.
