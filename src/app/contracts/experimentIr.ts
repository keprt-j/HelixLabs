export type FactorType = "continuous" | "categorical" | "ordinal" | "boolean";
export type ResponseObjective = "maximize" | "minimize" | "target";

export interface FactorSpec {
  name: string;
  type: FactorType;
  units?: string;
  bounds?: { min: number; max: number };
  levels?: Array<string | number | boolean>;
}

export interface ResponseSpec {
  name: string;
  objective: ResponseObjective;
  target_value?: number;
  units?: string;
  valid_range?: { min?: number; max?: number };
}

export interface ConstraintSpec {
  expression: string;
  severity?: "hard" | "soft";
}

export interface ProcedureStep {
  id: string;
  name: string;
  description?: string;
  expected_outputs?: string[];
}

export interface ExperimentIR {
  version: string;
  domain_hint?: string;
  hypothesis: {
    statement: string;
    confidence?: number;
    source_refs?: string[];
  };
  factors: FactorSpec[];
  responses: ResponseSpec[];
  constraints?: ConstraintSpec[];
  design: {
    strategy: string;
    sample_budget: number;
    replicates: number;
    random_seed?: number;
    noise_model?: string;
  };
  procedure_steps: ProcedureStep[];
  analysis_plan?: {
    primary_method?: string;
    secondary_methods?: string[];
  };
  provenance_refs?: string[];
}
