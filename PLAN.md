# PLAN.md — HelixLabs Final Product Architecture

## 1. Product Thesis

**HelixLabs is a cloud-lab operating system that compiles scientific intent into evidence-aware, non-redundant, scheduled, executable, validated, recoverable experiments, then recommends the next highest-value experiment.**

It is not a protocol generator, not a literature summarizer, and not a generic science chatbot. It is an operating layer for autonomous science.

Core loop:

```text
Parse → Search Prior Work → Compile → Validate → Schedule → Execute → Recover → Interpret → Iterate
```

---

## 2. One-Sentence Pitch

**HelixLabs checks whether an experiment has already been done, compiles the remaining scientific uncertainty into an executable lab run, schedules cloud-lab resources, recovers from failures, validates outputs, and recommends the next experiment.**

---

## 3. Final System Diagram

```text
Research Goal
   ↓
Scientific Intent Parser
   ↓
Live Literature + Prior Experiment Search
   ↓
Evidence Extraction + Experiment Matching
   ↓
Negative Results Memory
   ↓
Hypothesis + Claim Graph Builder
   ↓
Experiment IR Compiler
   ↓
Feasibility / Safety / Validity Validator
   ↓
Novelty + Redundancy + Value Scorer
   ↓
Protocol Generator
   ↓
Cloud-Lab Resource Scheduler
   ↓
Human Approval / Governance Gate
   ↓
Execution Adapter Layer
   ↓
Simulated or API-backed Lab Runner
   ↓
Failure Recovery Engine
   ↓
Data Stent: Schema Validation + Repair
   ↓
Result Interpreter
   ↓
Next Experiment Planner
   ↓
Provenance Report + Experiment Memory Update
```

---

## 4. Primary Demo Domain

Use **materials discovery**, specifically cobalt-free cathode optimization.

Canonical demo input:

> Find a low-cost cobalt-free cathode material and test whether Mn doping improves conductivity without hurting stability.

Canonical scientific story:

- Base candidate: LiFePO4.
- Intervention: Mn doping / manganese substitution.
- Prior low-Mn conditions were already tested.
- High-Mn condition failed stability.
- The unresolved scientific gap is the stability boundary between successful and failed Mn fractions.
- HelixLabs compiles a narrowed screen to locate the boundary.

---

## 5. Layer 1 — User Interface: HelixLabs Console

The frontend should be an experiment operations dashboard.

Required views:

1. Research Goal Input
2. Live Prior Work Search
3. Evidence / Experiment Match Review
4. Negative Results Memory
5. Claim Graph
6. Experiment IR
7. Feasibility + Novelty Scores
8. Protocol
9. Lab Schedule
10. Human Approval Gate
11. Execution Monitor
12. Failure Recovery
13. Data Stent Validation and Repair
14. Results + Next Experiment
15. Provenance Report

The user should see:

- What was asked.
- What prior work was found.
- What was already tested.
- What remains uncertain.
- What experiment HelixLabs compiled.
- Why the experiment is worth running.
- What resources it needs.
- What failed.
- How HelixLabs recovered.
- What the result means.
- What should be tested next.

---

## 6. Layer 2 — Scientific Intent Parser

Input:

```text
Find a low-cost cobalt-free cathode material and test whether Mn doping improves conductivity without hurting stability.
```

Output:

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
  ]
}
```

The parser should also produce search-ready synonyms:

```json
{
  "synonyms": {
    "Mn doping": ["manganese substitution", "Mn-substituted", "manganese-doped"],
    "LiFePO4": ["lithium iron phosphate", "LFP"]
  }
}
```

---

## 7. Layer 3 — Live Literature + Prior Experiment Search

The system must answer:

- Has this hypothesis already been tested?
- Was it tested under the same conditions?
- Were the results positive, negative, inconclusive, or contradictory?
- What exact parameter ranges were tested?
- What gap remains?
- Is the user’s proposed experiment redundant?

### External Search Sources

Use live search where possible:

- Semantic Scholar
- Crossref
- arXiv
- PubMed / NCBI E-utilities if relevant
- Domain-specific data sources when practical:
  - Materials Project
  - Open Reaction Database
  - protocols.io
  - WorkflowHub

### Cached Fallback

The demo must remain reliable if live APIs fail.

Include fallback data:

- `data/sample_literature.json`
- `data/sample_prior_runs.json`
- `data/sample_negative_results.json`

### Search Pipeline

```text
Experiment intent
   ↓
Query planner
   ↓
Multi-source literature retrieval
   ↓
Deduplication by DOI / PMID / arXiv ID / title similarity
   ↓
Abstract + metadata extraction
   ↓
Experiment-condition extraction
   ↓
Experiment equivalence matching
   ↓
Prior-work verdict
```

### Query Planner Example

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

---

## 8. Layer 4 — Evidence Extraction Engine

The evidence extraction layer turns papers and prior runs into structured experiment facts.

Extract:

- What was tested.
- Variables changed.
- Ranges tested.
- Controls used.
- Metrics measured.
- Result observed.
- Whether result supports, refutes, or partially supports the user hypothesis.
- Limitations stated.

Output:

```json
{
  "evidence_id": "EV-001",
  "source": {
    "type": "paper",
    "title": "Example paper title",
    "identifier": "DOI/PMID/arXiv/S2ID"
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

Distinguish:

- **Direct evidence:** same material, same intervention, same metric.
- **Analogous evidence:** similar material or related intervention.
- **Speculative inference:** model-generated reasoning not directly supported by a source.

---

## 9. Layer 5 — Prior Work Matching

The prior-work matcher compares experiment structures.

Matching fields:

- Material / organism / compound
- Intervention
- Variable range
- Controls
- Assay / measurement method
- Outcome metric
- Experimental conditions
- Result direction
- Confidence

Output:

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

---

## 10. Layer 6 — Negative Results Memory

Treat failed experiments as first-class data.

Negative result object:

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

Use cases:

- Avoid repeating known failures.
- Propose boundary-mapping experiments.
- Estimate risk.
- Improve scheduling priority.
- Improve next-experiment selection.

---

## 11. Layer 7 — Hypothesis + Claim Graph Builder

The claim graph turns the scientific goal into a structured reasoning object.

Output:

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

The agent should identify the weakest high-value claim and compile the experiment that tests it.

---

## 12. Layer 8 — Experiment IR Compiler

The Experiment IR is the central product object.

```text
Natural-language goal
→ evidence-aware scientific intent
→ Experiment IR
→ protocol
→ schedule
→ execution
→ result interpretation
```

Example:

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

The IR is the contract between AI reasoning and lab execution.

---

## 13. Layer 9 — Feasibility / Safety / Validity Validator

Validate the Experiment IR before protocol generation.

Checks:

- Are variables defined?
- Are units valid?
- Are controls present?
- Are metrics measurable?
- Are values plausible?
- Is the experiment redundant?
- Are required resources available?
- Is there a known negative result?
- Is the experiment within allowed risk/safety boundaries?
- Is the output schema defined?

Output:

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

For the hackathon, focus safety validation on feasibility, redundancy, units, controls, output schema, resource constraints, and risk flags. Avoid implementing complex regulated wet-lab safety logic.

---

## 14. Layer 10 — Novelty / Redundancy / Value Scorer

Scores:

- Novelty
- Redundancy
- Expected information gain
- Feasibility
- Cost
- Risk
- Dependency-unblocking value
- Resource burden

Output:

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

---

## 15. Layer 11 — Protocol Generator

Convert the Experiment IR into structured steps.

Output:

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

Support output formats:

- Human-readable protocol.
- Machine-readable JSON protocol.
- Opentrons-style pseudo-script.
- Cloud-lab API task payload.
- WorkflowHub / RO-Crate-style export, if time permits.

---

## 16. Layer 12 — Cloud-Lab Resource Scheduler

The scheduler manages:

- Resource availability
- Task dependencies
- Instrument capabilities
- Estimated duration
- Retries
- Priority
- Fairness
- User recent usage
- Scientific value
- Failure risk

Priority formula:

```text
priority_score =
  scientific_value
  + urgency
  + dependency_unblocking_score
  - user_recent_usage_penalty
  - resource_monopoly_penalty
  - expected_retry_cost
```

For the MVP, implement dependency-aware greedy scheduling.

Scheduler output:

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

---

## 17. Layer 13 — Human Approval / Governance Gate

Before execution, pause and show:

- Parsed hypothesis.
- Prior work found.
- Known negative results.
- Experiment novelty score.
- Redundancy score.
- Compiled experiment.
- Controls.
- Warnings.
- Resource schedule.
- Expected output schema.
- Failure recovery policy.

User choices:

- Approve run.
- Revise experiment.
- Cancel run.
- Force rerun despite redundancy.

---

## 18. Layer 14 — Execution Adapter Layer

HelixLabs should not be tied to one lab system.

Adapter interface:

```python
class ExecutionAdapter:
    def validate_task(self, task):
        pass

    def execute_task(self, task):
        pass

    def get_status(self, execution_id):
        pass

    def recover_from_error(self, task, error):
        pass
```

Adapters:

- SimulatedLabAdapter
- MaterialsProjectAdapter
- OpenReactionDatabaseAdapter
- MockOpentronsAdapter
- WorkflowHubAdapter
- Future real cloud-lab adapter

For the two-day build, prioritize SimulatedLabAdapter and optionally one live metadata/data adapter.

---

## 19. Layer 15 — Simulated or API-Backed Lab Runner

The lab runner executes scheduled tasks and returns logs/results.

Simulated output:

```csv
candidate_id,mn_pct,e_hull,cond_proxy,stable
LiFePO4_12,12,0.039,1.18,true
LiFePO4_14,14,0.046,1.22,true
LiFePO4_16,16,0.055,1.24,false
```

This intentionally includes schema drift.

---

## 20. Layer 16 — Failure Recovery Engine

Example failure:

```json
{
  "failure_type": "property_predictor_timeout",
  "affected_step": "S4",
  "affected_condition": "14_percent_Mn",
  "timestamp": "10:14"
}
```

Recovery options:

```json
{
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

---

## 21. Layer 17 — Data Stent: Validation + Repair

Expected schema:

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

Validation output:

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

Repaired output:

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

---

## 22. Layer 18 — Result Interpreter

The result interpreter separates:

- Observed result
- Prior evidence
- Model inference
- Uncertainty
- Limitations

Output:

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

---

## 23. Layer 19 — Next Experiment Planner

Scoring formula:

```text
experiment_value =
  expected_information_gain
  + novelty
  + feasibility
  + dependency_unblocking_score
  - cost
  - redundancy
  - risk
```

Output:

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

---

## 24. Layer 20 — Provenance Report + Experiment Memory Update

The provenance report includes:

- Original research goal
- Parsed scientific intent
- Live literature search queries
- Papers / prior runs retrieved
- Experiment match scores
- Negative results found
- Claim graph
- Experiment IR
- Feasibility warnings
- Novelty / redundancy / value scores
- Generated protocol
- Resource schedule
- Human approval event
- Execution log
- Failure recovery event
- Schema validation and repairs
- Observed results
- Inferences
- Uncertainty
- Next recommended experiment

After report generation, update:

- Completed experiment memory.
- Negative results memory.
- Known tested parameter ranges.
- Schema-repair patterns.
- Failure-recovery history.

---

## 25. Final State Machine

```text
CREATED
  ↓
GOAL_PARSED
  ↓
LITERATURE_SEARCHED
  ↓
PRIOR_WORK_MATCHED
  ↓
NEGATIVE_RESULTS_CHECKED
  ↓
CLAIM_GRAPH_BUILT
  ↓
EXPERIMENT_IR_COMPILED
  ↓
FEASIBILITY_VALIDATED
  ↓
NOVELTY_VALUE_SCORED
  ↓
PROTOCOL_GENERATED
  ↓
SCHEDULED
  ↓
AWAITING_HUMAN_APPROVAL
  ↓
APPROVED
  ↓
EXECUTING
  ↓
EXECUTION_FAILED_OR_COMPLETED
  ↓
RECOVERY_APPLIED
  ↓
RESULTS_COLLECTED
  ↓
RESULTS_VALIDATED
  ↓
RESULTS_REPAIRED
  ↓
INTERPRETED
  ↓
NEXT_EXPERIMENT_RECOMMENDED
  ↓
REPORT_GENERATED
  ↓
MEMORY_UPDATED
```

---

## 26. Backend API Design

Use FastAPI.

Required endpoints:

```text
POST /api/runs
GET  /api/runs/{run_id}

POST /api/runs/{run_id}/parse-goal
POST /api/runs/{run_id}/search-literature
POST /api/runs/{run_id}/match-prior-work
POST /api/runs/{run_id}/check-negative-results
POST /api/runs/{run_id}/build-claim-graph
POST /api/runs/{run_id}/compile-ir
POST /api/runs/{run_id}/validate-feasibility
POST /api/runs/{run_id}/score-value
POST /api/runs/{run_id}/generate-protocol
POST /api/runs/{run_id}/schedule
POST /api/runs/{run_id}/approve
POST /api/runs/{run_id}/execute
POST /api/runs/{run_id}/recover
POST /api/runs/{run_id}/validate-results
POST /api/runs/{run_id}/interpret
POST /api/runs/{run_id}/recommend-next
POST /api/runs/{run_id}/update-memory
GET  /api/runs/{run_id}/report
POST /api/runs/{run_id}/advance
```

---

## 27. Data Model

Minimum database tables:

- runs
- literature_searches
- retrieved_papers
- evidence_extractions
- prior_work_matches
- prior_runs
- negative_results
- claim_graphs
- experiment_ir
- validation_reports
- value_scores
- protocols
- lab_resources
- scheduled_tasks
- approval_events
- execution_logs
- failure_recoveries
- result_files
- schema_repairs
- interpretations
- next_experiments
- provenance_events

For the hackathon, many tables can be stored as JSON blobs.

Most important:

- runs
- retrieved_papers
- prior_work_matches
- experiment_ir
- protocols
- scheduled_tasks
- execution_logs
- schema_repairs
- next_experiments
- provenance_events

---

## 28. Recommended Repo Structure

```text
helixlabs/
  apps/
    web/
      components/
      pages/
      lib/
    api/
      main.py
      routes/
      db.py

  packages/
    agents/
      intent_parser.py
      claim_graph_builder.py
      evidence_extractor.py
      result_interpreter.py
      next_experiment_planner.py

    literature/
      query_planner.py
      semantic_scholar_client.py
      crossref_client.py
      pubmed_client.py
      arxiv_client.py
      deduplicator.py
      experiment_matcher.py

    prior_work/
      prior_checker.py
      negative_results.py
      experiment_memory.py

    compiler/
      experiment_ir.py
      compiler.py
      feasibility_validator.py
      value_scorer.py

    scheduler/
      resources.py
      scheduler.py
      fairness.py

    execution/
      adapters/
        base.py
        simulated_lab.py
        materials_project.py
        mock_opentrons.py
      runner.py
      recovery.py

    validation/
      schemas.py
      data_stent.py
      repair_engine.py

    provenance/
      event_log.py
      report_generator.py

  data/
    lab_resources.json
    sample_literature.json
    sample_prior_runs.json
    sample_negative_results.json
    expected_schemas/
      materials_screen_v1.json

  tests/
    test_literature_search.py
    test_experiment_matcher.py
    test_compiler.py
    test_scheduler.py
    test_data_stent.py
    test_state_machine.py
```

---

## 29. Two-Day Build Target

Must include:

1. Live literature search.
2. Paper/prior-run matching.
3. Negative results memory.
4. Claim graph.
5. Experiment IR compiler.
6. Feasibility validator.
7. Novelty/redundancy/value scoring.
8. Protocol generator.
9. Resource scheduler.
10. Human approval checkpoint.
11. Simulated execution.
12. Failure recovery.
13. Data stent validation and repair.
14. Result interpretation.
15. Next experiment planner.
16. Provenance report.

Use live + cached hybrid:

```text
Live search:
Semantic Scholar + Crossref + arXiv if practical

Cached fallback:
Curated papers/prior runs/negative results
```

---

## 30. Final Demo Narrative

User input:

```text
Find a low-cost cobalt-free cathode material and test whether Mn doping improves conductivity without hurting stability.
```

HelixLabs behavior:

1. Parses the goal into structured scientific intent.
2. Searches live literature and internal prior runs.
3. Finds low Mn fractions were already tested.
4. Finds a negative prior result at high Mn fraction.
5. Builds a claim graph.
6. Identifies the unresolved claim: the stability boundary between known successful and failed doping levels.
7. Compiles a narrowed experiment: 12%, 14%, 16% Mn.
8. Validates controls, metrics, resources, schema, and redundancy.
9. Scores the experiment as high-value and low-redundancy.
10. Generates a structured protocol.
11. Schedules simulated lab resources.
12. Requests human approval.
13. Executes the simulated run.
14. Recovers from a simulated timeout.
15. Detects schema drift in the result file.
16. Repairs the output data.
17. Interprets the result.
18. Recommends a boundary screen at 14.5%, 15.0%, and 15.5%.
19. Generates a complete provenance report.
20. Updates experiment memory.

Final conclusion:

```text
HelixLabs does not repeat the obvious experiment.
It discovers what has already been tested, identifies the unresolved scientific gap, runs the highest-value experiment, repairs broken outputs, and recommends the next run.
```

---

## 31. Judge-Facing Framing

### Novelty

HelixLabs is not a protocol generator. It is an experiment compiler and operating system for cloud labs.

It combines live prior-work search, claim graphs, experiment IR, resource scheduling, failure recovery, data repair, and next-experiment planning.

### Technical Difficulty

The system includes:

- Live literature retrieval
- Experiment equivalence matching
- Structured evidence extraction
- Stateful experiment orchestration
- Experiment IR compilation
- Resource scheduling
- Simulated execution
- Failure recovery
- Schema validation and repair
- Provenance logging
- Next-experiment optimization

### National Impact

The bottleneck in science is not only generating ideas. It is deciding which experiment is worth running, avoiding redundant work, coordinating scarce lab resources, recovering from failures, preserving negative results, and making autonomous experimentation auditable.

### Problem-Solution Fit

Researchers ask:

- Has this been done?
- What did prior work show?
- What remains uncertain?
- What experiment should I run?
- Can the lab execute it?
- What if it fails?
- What does the result mean?
- What should I do next?

HelixLabs answers that full chain.

---

## 32. Final Architecture Summary

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
