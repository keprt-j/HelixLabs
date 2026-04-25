from pathlib import Path

from conftest import fake_research_plan
from packages.compiler.compiler import compile_experiment_ir
from packages.compiler.feasibility_validator import validate_feasibility
from packages.compiler.value_scorer import score_experiment_value
from packages.workflow import CANONICAL_GOAL


def test_compiler_validator_and_scorer_match_demo_contract() -> None:
    root = Path(__file__).resolve().parents[1]
    plan = fake_research_plan(CANONICAL_GOAL)
    ir = compile_experiment_ir(plan)
    report = validate_feasibility(root, ir, plan=plan)
    score = score_experiment_value()

    assert ir.variables["mn_fraction"] == [0.12, 0.14, 0.16]
    assert "undoped_LiFePO4" in ir.controls
    assert report.validation_status == "passed_with_warnings"
    assert any("20% Mn" in issue.issue for issue in report.issues)
    assert score.overall_experiment_value > 0.8
