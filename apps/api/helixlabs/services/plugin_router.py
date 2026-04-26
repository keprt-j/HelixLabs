from __future__ import annotations

from dataclasses import dataclass

from helixlabs.domain.models import RunRecord
from helixlabs.services.plugins import ChemistryMaterialsPlugin, ExperimentPlugin, GenericBlackBoxPlugin


@dataclass
class PluginSelection:
    plugin: ExperimentPlugin
    confidence: float
    reason: str


class PluginRouter:
    def __init__(self, plugins: list[ExperimentPlugin] | None = None) -> None:
        self._plugins = plugins or [ChemistryMaterialsPlugin(), GenericBlackBoxPlugin()]

    def select(self, run: RunRecord) -> PluginSelection:
        scores: list[tuple[ExperimentPlugin, float]] = []
        for p in self._plugins:
            scores.append((p, max(0.0, min(1.0, float(p.can_handle(run))))))
        scores.sort(key=lambda x: x[1], reverse=True)
        plugin, score = scores[0]
        reason = f"Selected plugin '{plugin.plugin_id}' with confidence {score:.3f}"
        if plugin.plugin_id == "generic_blackbox":
            reason += " (fallback for low domain certainty)"
        return PluginSelection(plugin=plugin, confidence=score, reason=reason)

    def by_id(self, plugin_id: str) -> ExperimentPlugin | None:
        for p in self._plugins:
            if p.plugin_id == plugin_id:
                return p
        return None
