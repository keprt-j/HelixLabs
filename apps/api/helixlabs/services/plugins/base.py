from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from helixlabs.domain.models import RunRecord


class ExperimentPlugin(ABC):
    plugin_id: str

    @abstractmethod
    def can_handle(self, run: RunRecord) -> float:
        """Return confidence [0,1] that this plugin can execute the run."""

    @abstractmethod
    def compile_ir(self, run: RunRecord) -> dict[str, Any]:
        ...

    @abstractmethod
    def validate_feasibility(self, run: RunRecord, experiment_ir_artifact: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    def score_value(self, run: RunRecord, experiment_ir_artifact: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    def generate_protocol(self, run: RunRecord, experiment_ir_artifact: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    def schedule(self, run: RunRecord, experiment_ir_artifact: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    def execute(self, run: RunRecord, experiment_ir_artifact: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    def recover(self, run: RunRecord, execution_log: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    def validate_results(self, run: RunRecord, execution_log: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    def interpret(self, run: RunRecord, execution_log: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    def recommend_next(self, run: RunRecord, execution_log: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    def report(self, run: RunRecord, execution_log: dict[str, Any], interpretation: dict[str, Any]) -> dict[str, Any]:
        ...
