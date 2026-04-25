# API_CONTRACTS.md — HelixLabs Schemas and Endpoints

This document defines the core API contracts Codex should implement. Use Pydantic models in the backend and matching TypeScript types in the frontend where practical.

---

## 1. Run States

```text
CREATED
GOAL_PARSED
LITERATURE_SEARCHED
PRIOR_WORK_MATCHED
NEGATIVE_RESULTS_CHECKED
CLAIM_GRAPH_BUILT
EXPERIMENT_IR_COMPILED
FEASIBILITY_VALIDATED
NOVELTY_VALUE_SCORED
PROTOCOL_GENERATED
SCHEDULED
AWAITING_HUMAN_APPROVAL
APPROVED
EXECUTING
EXECUTION_FAILED_OR_COMPLETED
RECOVERY_APPLIED
RESULTS_COLLECTED
RESULTS_VALIDATED
RESULTS_REPAIRED
INTERPRETED
NEXT_EXPERIMENT_RECOMMENDED
REPORT_GENERATED
MEMORY_UPDATED
```

---

## 2. Core Models

### ExperimentRun

```json
{
  "id": "RUN-001",
  "title": "Cobalt-free cathode Mn-doping boundary screen",
  "domain": "materials_discovery",
  "state": "CREATED",
  "user_goal": "Find a low-cost cobalt-free cathode material and test whether Mn doping improves conductivity without hurting stability.",
  "created_at": "2026-04-25T10:00:00Z",
  "updated_at": "2026-04-25T10:00:00Z",
  "artifacts": {}
}
```

### ScientificIntent

```json
{
  "domain": "materials_discovery",
  "objective": "optimize_cobalt_free_cathode",
  "base_material": "LiFePO4",
  "intervention": "Mn doping",
  "target_property": "conductivity_proxy",
  "must_preserve": "thermodynamic_stability",
  "constraints": {
    "exclude_elements": ["Co", "Ni"],
    "prefer_low_cost": true,
    "max_runtime_hours": 4
  },
  "success_metrics": [
    "energy_above_hull",
    "conductivity_proxy",
    "stability_pass"
  ],
  "primary_question": "Does moderate Mn doping improve conductivity while preserving stability?",
  "search_entities": [
    "LiFePO4",
    "lithium iron phosphate",
    "Mn doping",
    "manganese substitution",
    "cathode",
    "conductivity",
    "stability"
  ],
  "synonyms": {
    "Mn doping": ["manganese substitution", "Mn-substituted", "manganese-doped"],
    "LiFePO4": ["lithium iron phosphate", "LFP"]
  }
}
```

### LiteratureQueryPlan

```json
{
  "exact_queries": [
    "\"LiFePO4\" \"Mn doping\" conductivity stability",
    "\"lithium iron phosphate\" manganese substitution cathode"
  ],
  "broad_queries": [
    "manganese doped lithium iron phosphate cathode conductivity",
    "LiFePO4 dopant screen structural stability"
  ],
  "negative_result_queries": [
    "LiFePO4 Mn doping instability",
    "manganese substituted LiFePO4 failed stability"
  ],
  "protocol_queries": [
    "LiFePO4 manganese doping synthesis protocol",
    "lithium iron phosphate dopant screening method"
  ]
}
```

### RetrievedPaper

```json
{
  "paper_id": "S2-123",
  "title": "Manganese-substituted lithium iron phosphate cathodes",
  "abstract": "This paper studies Mn substitution in LiFePO4 cathode materials...",
  "authors": ["A. Researcher", "B. Scientist"],
  "year": 2022,
  "venue": "Journal of Example Materials",
  "doi": "10.0000/example",
  "url": "https://example.org/paper",
  "source": "semantic_scholar",
  "retrieval_mode": "live"
}
```

### EvidenceExtraction

```json
{
  "evidence_id": "EV-001",
  "source": {
    "type": "paper",
    "title": "Manganese-substituted lithium iron phosphate cathodes",
    "identifier": "10.0000/example"
  },
  "experiment_facts": {
    "material": "LiFePO4",
    "intervention": "Mn doping",
    "variable": "mn_fraction",
    "tested_values": [0.0, 0.05, 0.10],
    "measured_properties": ["conductivity", "stability"],
    "reported_outcome": "10% Mn improved conductivity while retaining stability"
  },
  "match_to_user_hypothesis": {
    "overlap": "high",
    "redundancy_contribution": 0.58,
    "novelty_gap": "No results between 10% and 20%"
  }
}
```

### PriorWorkMatch

```json
{
  "prior_work_status": "partially_tested",
  "matches": [
    {
      "source_type": "paper",
      "title": "Manganese-substituted lithium iron phosphate cathodes",
      "identifier": "doi_or_paper_id",
      "overlap": "high",
      "tested_conditions": ["0%", "5%", "10% Mn"],
      "reported_result": "low Mn substitution improved conductivity while preserving stability",
      "evidence_strength": 0.81
    },
    {
      "source_type": "internal_prior_run",
      "source_id": "R-021",
      "overlap": "medium",
      "tested_conditions": ["20% Mn"],
      "reported_result": "20% Mn failed stability threshold",
      "evidence_strength": 0.93
    }
  ],
  "gap": "The stability boundary between 10% and 20% Mn remains unresolved.",
  "recommendation": "Run a narrowed screen around 12–16% Mn instead of repeating the full range."
}
```

### NegativeResult

```json
{
  "negative_result_id": "NR-021",
  "experiment": "LiFePO4 Mn doping",
  "failed_condition": "20% Mn",
  "failure_type": "stability_threshold_failed",
  "observed_result": {
    "energy_above_hull": 0.071,
    "stability_pass": false
  },
  "recommendation": "Avoid testing above 18% Mn unless mapping the failure boundary.",
  "source": "internal_run_R-021"
}
```

### ClaimGraph

```json
{
  "main_hypothesis": "Moderate Mn doping improves LiFePO4 conductivity while preserving stability.",
  "claims": [
    {
      "id": "C1",
      "claim": "LiFePO4 is a feasible cobalt-free cathode candidate.",
      "status": "supported",
      "evidence": ["materials_database", "literature_search"]
    },
    {
      "id": "C2",
      "claim": "Low Mn doping improves conductivity.",
      "status": "partially_supported",
      "evidence": ["paper_match_001", "internal_run_R-017"]
    },
    {
      "id": "C3",
      "claim": "Mn substitution remains stable above 10% and below 20%.",
      "status": "uncertain",
      "evidence": ["internal_run_R-017", "negative_result_R-021"]
    }
  ],
  "weakest_high_value_claim": "C3"
}
```

### ExperimentIR

```json
{
  "experiment_id": "EXP-001",
  "domain": "materials_discovery",
  "hypothesis": "Moderate Mn doping improves conductivity while preserving stability.",
  "target_claim": "C3",
  "experiment_type": "dopant_boundary_screen",
  "material": "LiFePO4",
  "variables": {
    "mn_fraction": [0.12, 0.14, 0.16]
  },
  "controls": [
    "undoped_LiFePO4",
    "10_percent_Mn_prior_baseline"
  ],
  "success_metrics": [
    "energy_above_hull",
    "conductivity_proxy",
    "stability_pass"
  ],
  "constraints": {
    "stability_threshold_ev": 0.05,
    "exclude_elements": ["Co", "Ni"],
    "max_runtime_hours": 4
  },
  "evidence_context": {
    "already_tested": [0.0, 0.05, 0.10, 0.20],
    "unresolved_gap": "12–16% Mn stability boundary"
  },
  "required_resources": [
    "simulated_synthesis_station",
    "structure_validator",
    "property_predictor",
    "data_validation_engine"
  ],
  "expected_output_schema": "materials_screen_v1"
}
```

### FeasibilityReport

```json
{
  "validation_status": "passed_with_warnings",
  "issues": [
    {
      "severity": "info",
      "issue": "0%, 5%, and 10% Mn were already tested.",
      "resolution": "Excluded redundant low-fraction conditions."
    },
    {
      "severity": "warning",
      "issue": "20% Mn previously failed stability.",
      "resolution": "Avoided 20% and selected 12–16% boundary screen."
    }
  ],
  "approved_for_protocol_generation": true
}
```

### ExperimentValueScore

```json
{
  "prior_work_status": "partially_tested",
  "redundancy_score": 0.21,
  "novelty_score": 0.78,
  "expected_information_gain": 0.84,
  "feasibility_score": 0.91,
  "resource_cost": 0.32,
  "risk_score": 0.27,
  "overall_experiment_value": 0.82,
  "recommendation": "Proceed with narrowed screen."
}
```

### Protocol

```json
{
  "protocol_id": "P-001",
  "name": "Narrow Mn-doping boundary screen for LiFePO4",
  "steps": [
    {
      "step_id": "S1",
      "name": "Prepare candidate batches",
      "resource_type": "simulated_synthesis_station",
      "duration_minutes": 20,
      "depends_on": []
    },
    {
      "step_id": "S2",
      "name": "Run simulated synthesis",
      "resource_type": "simulated_synthesis_station",
      "duration_minutes": 30,
      "depends_on": ["S1"]
    },
    {
      "step_id": "S3",
      "name": "Validate structure",
      "resource_type": "structure_validator",
      "duration_minutes": 15,
      "depends_on": ["S2"]
    },
    {
      "step_id": "S4",
      "name": "Predict stability and conductivity proxy",
      "resource_type": "property_predictor",
      "duration_minutes": 15,
      "depends_on": ["S3"]
    },
    {
      "step_id": "S5",
      "name": "Validate result schema",
      "resource_type": "data_validation_engine",
      "duration_minutes": 5,
      "depends_on": ["S4"]
    }
  ]
}
```

### LabResource

```json
{
  "resource_id": "synth_01",
  "type": "simulated_synthesis_station",
  "available_at": "09:00",
  "capabilities": ["prepare_batch", "simulate_synthesis"],
  "status": "available"
}
```

### Schedule

```json
{
  "schedule_id": "SCH-001",
  "scheduled_tasks": [
    {
      "step_id": "S1",
      "resource_id": "synth_01",
      "start": "09:00",
      "end": "09:20"
    },
    {
      "step_id": "S2",
      "resource_id": "synth_01",
      "start": "09:20",
      "end": "09:50"
    },
    {
      "step_id": "S3",
      "resource_id": "validator_01",
      "start": "09:50",
      "end": "10:05"
    },
    {
      "step_id": "S4",
      "resource_id": "predictor_01",
      "start": "10:05",
      "end": "10:20"
    },
    {
      "step_id": "S5",
      "resource_id": "data_validator_01",
      "start": "10:20",
      "end": "10:25"
    }
  ]
}
```

### ApprovalEvent

```json
{
  "approval_id": "APP-001",
  "run_id": "RUN-001",
  "approved": true,
  "approved_by": "demo_user",
  "timestamp": "2026-04-25T10:12:00Z",
  "notes": "Approved narrowed screen after prior-work check."
}
```

### ExecutionLog

```json
{
  "execution_id": "EXE-001",
  "status": "completed_with_recovery",
  "events": [
    {
      "timestamp": "10:05",
      "step_id": "S4",
      "event_type": "started",
      "message": "Property prediction started."
    },
    {
      "timestamp": "10:14",
      "step_id": "S4",
      "event_type": "failure",
      "message": "Property predictor timeout for 14% Mn condition."
    }
  ],
  "raw_result_csv": "candidate_id,mn_pct,e_hull,cond_proxy,stable\nLiFePO4_12,12,0.039,1.18,true\nLiFePO4_14,14,0.046,1.22,true\nLiFePO4_16,16,0.055,1.24,false"
}
```

### FailureRecoveryPlan

```json
{
  "failure_type": "property_predictor_timeout",
  "affected_step": "S4",
  "affected_condition": "14_percent_Mn",
  "recovery_options": [
    {
      "action": "retry_failed_condition",
      "cost_minutes": 8,
      "data_loss": "none",
      "score": 0.91
    },
    {
      "action": "skip_failed_condition",
      "cost_minutes": 0,
      "data_loss": "14_percent_Mn_missing",
      "score": 0.42
    },
    {
      "action": "rerun_full_experiment",
      "cost_minutes": 65,
      "data_loss": "none",
      "score": 0.28
    }
  ],
  "selected_recovery": "retry_failed_condition"
}
```

### ResultSchema

```json
{
  "schema_id": "materials_screen_v1",
  "fields": [
    {"name": "candidate_id", "type": "string"},
    {"name": "mn_fraction", "type": "number"},
    {"name": "energy_above_hull", "type": "number"},
    {"name": "conductivity_proxy", "type": "number"},
    {"name": "stability_pass", "type": "boolean"}
  ]
}
```

### ValidationReport

```json
{
  "valid": false,
  "issues": [
    {
      "type": "column_name_mismatch",
      "expected": "mn_fraction",
      "found": "mn_pct",
      "repair": "map mn_pct to mn_fraction and divide by 100"
    },
    {
      "type": "column_name_mismatch",
      "expected": "energy_above_hull",
      "found": "e_hull",
      "repair": "map e_hull to energy_above_hull"
    },
    {
      "type": "column_name_mismatch",
      "expected": "conductivity_proxy",
      "found": "cond_proxy",
      "repair": "map cond_proxy to conductivity_proxy"
    },
    {
      "type": "column_name_mismatch",
      "expected": "stability_pass",
      "found": "stable",
      "repair": "map stable to stability_pass"
    }
  ],
  "repair_status": "applied"
}
```

### RepairedResults

```json
[
  {
    "candidate_id": "LiFePO4_12",
    "mn_fraction": 0.12,
    "energy_above_hull": 0.039,
    "conductivity_proxy": 1.18,
    "stability_pass": true
  },
  {
    "candidate_id": "LiFePO4_14",
    "mn_fraction": 0.14,
    "energy_above_hull": 0.046,
    "conductivity_proxy": 1.22,
    "stability_pass": true
  },
  {
    "candidate_id": "LiFePO4_16",
    "mn_fraction": 0.16,
    "energy_above_hull": 0.055,
    "conductivity_proxy": 1.24,
    "stability_pass": false
  }
]
```

### ResultInterpretation

```json
{
  "observed_results": [
    "12% Mn passed stability threshold and improved conductivity proxy.",
    "14% Mn passed stability threshold and improved conductivity proxy.",
    "16% Mn failed stability threshold despite a higher conductivity proxy."
  ],
  "prior_evidence": [
    "0%, 5%, and 10% Mn had already been tested.",
    "20% Mn previously failed stability."
  ],
  "inference": "The useful Mn-doping region likely lies between 12% and 15%.",
  "uncertainty": "The exact stability boundary between 14% and 16% remains unresolved.",
  "limitations": [
    "Results come from simulated property predictions.",
    "Physical synthesis feasibility would need validation."
  ]
}
```

### NextExperimentRecommendation

```json
{
  "candidate_next_experiments": [
    {
      "name": "Boundary screen between 14% and 16% Mn",
      "conditions": [0.145, 0.150, 0.155],
      "expected_information_gain": 0.91,
      "novelty": 0.83,
      "feasibility": 0.88,
      "redundancy": 0.12,
      "cost": 0.25,
      "risk": 0.30,
      "score": 0.82
    },
    {
      "name": "Repeat 12–16% screen",
      "conditions": [0.12, 0.14, 0.16],
      "expected_information_gain": 0.35,
      "novelty": 0.21,
      "feasibility": 0.95,
      "redundancy": 0.78,
      "cost": 0.40,
      "risk": 0.20,
      "score": 0.19
    }
  ],
  "selected_next_experiment": "Boundary screen between 14% and 16% Mn",
  "rationale": "14% passed and 16% failed, so the highest-value next experiment is to locate the stability boundary."
}
```

### ProvenanceEvent

```json
{
  "event_id": "PE-001",
  "run_id": "RUN-001",
  "timestamp": "2026-04-25T10:20:00Z",
  "event_type": "schema_repair",
  "summary": "Mapped e_hull to energy_above_hull and mn_pct to mn_fraction.",
  "actor": "data_stent",
  "payload": {}
}
```

### ProvenanceReport

```json
{
  "run_id": "RUN-001",
  "title": "HelixLabs Experiment Report",
  "sections": [
    {
      "title": "Research Goal",
      "content": "Find a low-cost cobalt-free cathode material and test whether Mn doping improves conductivity without hurting stability."
    },
    {
      "title": "Prior Work",
      "content": "Low Mn fractions were previously tested; 20% Mn failed stability."
    },
    {
      "title": "Next Experiment",
      "content": "Boundary screen between 14% and 16% Mn."
    }
  ],
  "provenance_events": []
}
```

---

## 3. API Endpoints

### Create Run

```http
POST /api/runs
```

Request:

```json
{
  "user_goal": "Find a low-cost cobalt-free cathode material and test whether Mn doping improves conductivity without hurting stability."
}
```

Response:

```json
{
  "run": {
    "id": "RUN-001",
    "state": "CREATED",
    "user_goal": "Find a low-cost cobalt-free cathode material and test whether Mn doping improves conductivity without hurting stability."
  }
}
```

### Get Run

```http
GET /api/runs/{run_id}
```

Response:

```json
{
  "run": {},
  "artifacts": {},
  "provenance_events": []
}
```

### Advance Run

```http
POST /api/runs/{run_id}/advance
```

Response:

```json
{
  "run_id": "RUN-001",
  "previous_state": "CREATED",
  "new_state": "GOAL_PARSED",
  "artifact_created": "scientific_intent"
}
```

### Parse Goal

```http
POST /api/runs/{run_id}/parse-goal
```

Response:

```json
{
  "scientific_intent": {}
}
```

### Search Literature

```http
POST /api/runs/{run_id}/search-literature
```

Response:

```json
{
  "query_plan": {},
  "retrieved_papers": [],
  "retrieval_mode": "live_or_fallback"
}
```

### Match Prior Work

```http
POST /api/runs/{run_id}/match-prior-work
```

Response:

```json
{
  "evidence_extractions": [],
  "prior_work_match": {}
}
```

### Check Negative Results

```http
POST /api/runs/{run_id}/check-negative-results
```

Response:

```json
{
  "negative_results": []
}
```

### Build Claim Graph

```http
POST /api/runs/{run_id}/build-claim-graph
```

Response:

```json
{
  "claim_graph": {}
}
```

### Compile IR

```http
POST /api/runs/{run_id}/compile-ir
```

Response:

```json
{
  "experiment_ir": {}
}
```

### Validate Feasibility

```http
POST /api/runs/{run_id}/validate-feasibility
```

Response:

```json
{
  "feasibility_report": {}
}
```

### Score Value

```http
POST /api/runs/{run_id}/score-value
```

Response:

```json
{
  "value_score": {}
}
```

### Generate Protocol

```http
POST /api/runs/{run_id}/generate-protocol
```

Response:

```json
{
  "protocol": {}
}
```

### Schedule

```http
POST /api/runs/{run_id}/schedule
```

Response:

```json
{
  "schedule": {}
}
```

### Approve

```http
POST /api/runs/{run_id}/approve
```

Request:

```json
{
  "approved": true,
  "approved_by": "demo_user",
  "notes": "Approved narrowed screen."
}
```

Response:

```json
{
  "approval_event": {},
  "state": "APPROVED"
}
```

### Execute

```http
POST /api/runs/{run_id}/execute
```

Response:

```json
{
  "execution_log": {},
  "state": "EXECUTION_FAILED_OR_COMPLETED"
}
```

### Recover

```http
POST /api/runs/{run_id}/recover
```

Response:

```json
{
  "failure_recovery_plan": {},
  "state": "RECOVERY_APPLIED"
}
```

### Validate Results

```http
POST /api/runs/{run_id}/validate-results
```

Response:

```json
{
  "validation_report": {},
  "repaired_results": []
}
```

### Interpret

```http
POST /api/runs/{run_id}/interpret
```

Response:

```json
{
  "interpretation": {}
}
```

### Recommend Next

```http
POST /api/runs/{run_id}/recommend-next
```

Response:

```json
{
  "next_experiment_recommendation": {}
}
```

### Update Memory

```http
POST /api/runs/{run_id}/update-memory
```

Response:

```json
{
  "memory_updated": true,
  "updated_records": []
}
```

### Get Report

```http
GET /api/runs/{run_id}/report
```

Response:

```json
{
  "report": {}
}
```

---

## 4. Error Response Shape

Use this error shape consistently:

```json
{
  "error": {
    "code": "INVALID_STATE_TRANSITION",
    "message": "Run must be approved before execution.",
    "details": {
      "current_state": "AWAITING_HUMAN_APPROVAL",
      "required_state": "APPROVED"
    }
  }
}
```
