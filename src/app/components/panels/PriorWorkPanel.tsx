import { AlertCircle, CheckCircle2 } from "lucide-react";

export function PriorWorkPanel() {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-green-100/30 border border-green-700 rounded-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle2 className="w-4 h-4 text-green-700" />
            <h3 className="text-sm text-green-800">Already Tested</h3>
          </div>
          <div className="space-y-2">
            <div className="text-stone-700 text-sm">
              <span className="font-mono text-stone-900">Run #1247</span> — Al-doped LLZO
            </div>
            <div className="text-stone-700 text-sm">
              <span className="font-mono text-stone-900">Run #1289</span> — Ta-doped LLZO
            </div>
            <div className="text-stone-700 text-sm">
              <span className="font-mono text-stone-900">Run #1301</span> — Nb-doped LLZO
            </div>
          </div>
        </div>

        <div className="bg-yellow-100/40 border border-yellow-700 rounded-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <AlertCircle className="w-4 h-4 text-yellow-700" />
            <h3 className="text-sm text-yellow-800">Untested</h3>
          </div>
          <div className="space-y-2">
            <div className="text-stone-700 text-sm">Fe-doped LLZO</div>
            <div className="text-stone-700 text-sm">Co-doped LLZO</div>
            <div className="text-stone-700 text-sm">Ni-doped LLZO</div>
            <div className="text-stone-700 text-sm">Temperature sweep &gt;250°C</div>
          </div>
        </div>
      </div>

      <div className="bg-yellow-50/50 border border-amber-200 rounded-lg p-6">
        <h3 className="text-sm text-stone-600 mb-4">Overlap Analysis</h3>

        <div className="grid grid-cols-2 gap-6">
          <div>
            <div className="text-xs text-stone-600 mb-1 font-mono">NOVELTY SCORE</div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl text-green-700">7.2</span>
              <span className="text-stone-600">/10</span>
            </div>
          </div>

          <div>
            <div className="text-xs text-stone-600 mb-1 font-mono">REDUNDANCY SCORE</div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl text-yellow-700">3.1</span>
              <span className="text-stone-600">/10</span>
            </div>
          </div>
        </div>

        <div className="mt-6 p-4 bg-blue-100/40 border border-blue-700 rounded">
          <div className="text-xs text-blue-800 mb-1 font-mono">RECOMMENDATION</div>
          <div className="text-stone-900">
            Proceed with Fe-doped variant. Similar composition space but unexplored dopant.
            Modify temperature range to include 250-300°C for completeness.
          </div>
        </div>
      </div>

      <div className="bg-yellow-50/50 border border-amber-200 rounded-lg p-6">
        <h3 className="text-sm text-stone-600 mb-4">Prior Evidence</h3>

        <div className="space-y-3">
          <div className="flex items-start gap-3 p-3 bg-amber-50/50 rounded">
            <div className="text-xs text-stone-600 font-mono mt-0.5">RUN #1247</div>
            <div className="flex-1">
              <div className="text-sm text-stone-900 mb-1">Al-doped LLZO (5 mol%)</div>
              <div className="text-xs text-stone-600">σ = 2.4×10⁻⁴ S/cm @ 25°C</div>
            </div>
          </div>

          <div className="flex items-start gap-3 p-3 bg-amber-50/50 rounded">
            <div className="text-xs text-stone-600 font-mono mt-0.5">RUN #1289</div>
            <div className="flex-1">
              <div className="text-sm text-stone-900 mb-1">Ta-doped LLZO (3 mol%)</div>
              <div className="text-xs text-stone-600">σ = 3.1×10⁻⁴ S/cm @ 25°C</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
