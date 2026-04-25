import { TrendingUp, AlertCircle } from "lucide-react";

export function NextExperimentPanel() {
  return (
    <div className="space-y-4">
      <div className="bg-blue-100/40 border border-blue-700 rounded-lg p-6">
        <div className="flex items-start gap-3 mb-4">
          <TrendingUp className="w-6 h-6 text-blue-700 flex-shrink-0" />
          <div>
            <h3 className="text-lg text-blue-800 mb-2">Recommended Next Experiment</h3>
            <div className="text-stone-900">
              Fine-grained Fe concentration sweep around optimal range
            </div>
          </div>
        </div>

        <div className="mt-6 space-y-4">
          <div>
            <div className="text-xs text-stone-600 mb-2 font-mono">RATIONALE</div>
            <div className="text-stone-900">
              Current results show peak performance at 5 mol% Fe, but coarse sampling (0.1, 0.5, 1.0, 3.0, 5.0)
              may miss true optimum. Narrow sweep between 3-7 mol% will identify precise peak concentration.
            </div>
          </div>

          <div>
            <div className="text-xs text-stone-600 mb-2 font-mono">PROPOSED VARIABLES</div>
            <div className="space-y-2">
              <div className="flex items-center justify-between p-2 bg-yellow-50/50 rounded">
                <span className="text-stone-700 font-mono text-sm">dopant_type</span>
                <span className="text-stone-600">Fe (fixed)</span>
              </div>
              <div className="flex items-center justify-between p-2 bg-yellow-50/50 rounded">
                <span className="text-stone-700 font-mono text-sm">dopant_concentration</span>
                <span className="text-stone-600">[3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0] mol%</span>
              </div>
              <div className="flex items-center justify-between p-2 bg-yellow-50/50 rounded">
                <span className="text-stone-700 font-mono text-sm">temperature</span>
                <span className="text-stone-600">[25, 100, 200, 300] °C (reduced set)</span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-yellow-50/50 rounded">
              <div className="text-xs text-stone-600 mb-1 font-mono">EXPECTED INFO GAIN</div>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl text-green-700">8.4</span>
                <span className="text-stone-600">/10</span>
              </div>
              <div className="text-xs text-stone-600 mt-1">High potential for optimization</div>
            </div>

            <div className="p-4 bg-yellow-50/50 rounded">
              <div className="text-xs text-stone-600 mb-1 font-mono">RISK LEVEL</div>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl text-yellow-700">3.2</span>
                <span className="text-stone-600">/10</span>
              </div>
              <div className="text-xs text-stone-600 mt-1">Low risk, established method</div>
            </div>
          </div>

          <div>
            <div className="text-xs text-stone-600 mb-2 font-mono">ESTIMATED RESOURCES</div>
            <div className="grid grid-cols-2 gap-2">
              <div className="flex items-center justify-between p-2 bg-yellow-50/50 rounded text-sm">
                <span className="text-stone-700">Duration</span>
                <span className="text-stone-900">24 hours</span>
              </div>
              <div className="flex items-center justify-between p-2 bg-yellow-50/50 rounded text-sm">
                <span className="text-stone-700">Samples</span>
                <span className="text-stone-900">9 compositions</span>
              </div>
              <div className="flex items-center justify-between p-2 bg-yellow-50/50 rounded text-sm">
                <span className="text-stone-700">Cost</span>
                <span className="text-stone-900">$420 materials</span>
              </div>
              <div className="flex items-center justify-between p-2 bg-yellow-50/50 rounded text-sm">
                <span className="text-stone-700">Measurements</span>
                <span className="text-stone-900">36 data points</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-yellow-50/50 border border-amber-200 rounded-lg p-6">
        <h3 className="text-sm text-stone-600 mb-4">Alternative Directions</h3>

        <div className="space-y-3">
          <div className="p-4 bg-amber-50/50 border border-amber-200 rounded">
            <div className="text-stone-900 mb-2">Co-doping study (Fe + Ta)</div>
            <div className="text-sm text-stone-700 mb-3">
              Investigate synergistic effects of dual dopants
            </div>
            <div className="flex gap-4 text-xs">
              <span className="text-green-700">Info gain: 7.8</span>
              <span className="text-yellow-700">Risk: 5.1</span>
            </div>
          </div>

          <div className="p-4 bg-amber-50/50 border border-amber-200 rounded">
            <div className="text-stone-900 mb-2">Long-term stability test</div>
            <div className="text-sm text-stone-700 mb-3">
              Verify conductivity retention over 1000 hours
            </div>
            <div className="flex gap-4 text-xs">
              <span className="text-green-700">Info gain: 6.2</span>
              <span className="text-yellow-700">Risk: 2.8</span>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-yellow-100/50 border border-yellow-700 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-yellow-700 mt-0.5 flex-shrink-0" />
          <div>
            <div className="text-sm text-yellow-800 mb-1">Decision Point</div>
            <div className="text-sm text-stone-900">
              Current hypothesis is well-supported. Consider pursuing optimization (narrow sweep)
              or exploring new claims (co-doping, stability).
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
