from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from helixlabs.domain.models import ExperimentIR, FactorType


class ExperimentIRValidator:
    """Structural + lightweight semantic checks for universal IR."""

    def validate(self, candidate: dict[str, Any]) -> dict[str, Any]:
        errors: list[dict[str, Any]] = []
        warnings: list[dict[str, Any]] = []
        normalized: dict[str, Any] | None = None

        try:
            model = ExperimentIR.model_validate(candidate)
            normalized = model.model_dump()
        except ValidationError as exc:
            for e in exc.errors():
                errors.append(
                    {
                        "path": "/".join(str(x) for x in e.get("loc", [])),
                        "message": e.get("msg", "invalid field"),
                        "type": e.get("type", "validation_error"),
                    }
                )
            return {"is_valid": False, "errors": errors, "warnings": warnings, "normalized_ir": None}

        for idx, factor in enumerate(model.factors):
            if factor.type == FactorType.CONTINUOUS:
                if not factor.bounds:
                    errors.append(
                        {
                            "path": f"factors/{idx}/bounds",
                            "message": "continuous factor must define bounds",
                            "type": "semantic_error",
                        }
                    )
                else:
                    lo = factor.bounds.get("min")
                    hi = factor.bounds.get("max")
                    if lo is None or hi is None or lo >= hi:
                        errors.append(
                            {
                                "path": f"factors/{idx}/bounds",
                                "message": "continuous factor bounds require min < max",
                                "type": "semantic_error",
                            }
                        )
            else:
                if not factor.levels:
                    warnings.append(
                        {
                            "path": f"factors/{idx}/levels",
                            "message": "non-continuous factor has no explicit levels",
                            "type": "completeness_warning",
                        }
                    )

        sample_budget = model.design.get("sample_budget")
        replicates = model.design.get("replicates")
        if isinstance(sample_budget, int) and isinstance(replicates, int):
            if sample_budget < replicates:
                errors.append(
                    {
                        "path": "design/sample_budget",
                        "message": "sample_budget should be >= replicates",
                        "type": "semantic_error",
                    }
                )
            if sample_budget > 5000:
                warnings.append(
                    {
                        "path": "design/sample_budget",
                        "message": "very large sample budget may be impractical",
                        "type": "scale_warning",
                    }
                )

        for idx, response in enumerate(model.responses):
            if response.objective.value == "target" and response.target_value is None:
                warnings.append(
                    {
                        "path": f"responses/{idx}/target_value",
                        "message": "target objective usually requires target_value",
                        "type": "completeness_warning",
                    }
                )

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "normalized_ir": normalized,
        }
