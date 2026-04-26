from __future__ import annotations

import unittest

from helixlabs.services.ir_validator import ExperimentIRValidator


class ExperimentIRValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = ExperimentIRValidator()

    def _base_ir(self) -> dict:
        return {
            "version": "1.0",
            "domain_hint": "generic",
            "hypothesis": {"statement": "x affects y"},
            "factors": [
                {
                    "name": "x",
                    "type": "continuous",
                    "bounds": {"min": 0.0, "max": 1.0},
                    "levels": [0.0, 0.5, 1.0],
                }
            ],
            "responses": [{"name": "y", "objective": "maximize"}],
            "design": {"strategy": "grid", "sample_budget": 12, "replicates": 2},
            "procedure_steps": [{"id": "s1", "name": "run"}],
        }

    def test_valid_ir_passes(self):
        out = self.validator.validate(self._base_ir())
        self.assertTrue(out["is_valid"])
        self.assertEqual(len(out["errors"]), 0)
        self.assertIsNotNone(out["normalized_ir"])

    def test_continuous_factor_requires_bounds(self):
        ir = self._base_ir()
        ir["factors"][0].pop("bounds")
        out = self.validator.validate(ir)
        self.assertFalse(out["is_valid"])
        self.assertTrue(any("bounds" in e["path"] for e in out["errors"]))

    def test_sample_budget_less_than_replicates_is_error(self):
        ir = self._base_ir()
        ir["design"]["sample_budget"] = 1
        ir["design"]["replicates"] = 4
        out = self.validator.validate(ir)
        self.assertFalse(out["is_valid"])
        self.assertTrue(any(e["path"] == "design/sample_budget" for e in out["errors"]))

    def test_target_response_without_target_value_warns(self):
        ir = self._base_ir()
        ir["responses"] = [{"name": "y", "objective": "target"}]
        out = self.validator.validate(ir)
        self.assertTrue(out["is_valid"])
        self.assertTrue(any("target_value" in w["path"] for w in out["warnings"]))


if __name__ == "__main__":
    unittest.main()
