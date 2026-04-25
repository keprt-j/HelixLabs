import { ArrowDown } from "lucide-react";

export function ClaimGraphPanel() {
  return (
    <div className="bg-yellow-50/50 border border-amber-200 rounded-lg p-6">
      <h3 className="text-sm text-stone-600 mb-6">Hypothesis Tree</h3>

      <div className="space-y-4">
        <div className="border border-green-700 bg-green-100/40 rounded-lg p-4">
          <div className="flex items-start justify-between mb-2">
            <div className="text-stone-900">
              Fe doping will improve ionic conductivity of LLZO
            </div>
            <div className="px-2 py-0.5 bg-green-700 text-green-100 text-xs rounded">
              Supported
            </div>
          </div>
          <div className="text-xs text-stone-600 font-mono">MAIN HYPOTHESIS</div>
        </div>

        <div className="flex justify-center">
          <ArrowDown className="w-4 h-4 text-stone-600" />
        </div>

        <div className="ml-8 space-y-3">
          <div className="border border-yellow-700 bg-yellow-100/40 rounded-lg p-4">
            <div className="flex items-start justify-between mb-2">
              <div className="text-stone-900 text-sm">
                Fe²⁺ substitutes for Li⁺ sites
              </div>
              <div className="px-2 py-0.5 bg-yellow-700 text-yellow-100 text-xs rounded">
                Uncertain
              </div>
            </div>
            <div className="text-xs text-stone-600 font-mono">SUB-CLAIM 1</div>
          </div>

          <div className="border border-amber-300 bg-amber-50/50 rounded-lg p-4">
            <div className="flex items-start justify-between mb-2">
              <div className="text-stone-900 text-sm">
                Defect concentration increases with dopant %
              </div>
              <div className="px-2 py-0.5 bg-amber-700 text-amber-100 text-xs rounded">
                Untested
              </div>
            </div>
            <div className="text-xs text-stone-600 font-mono">SUB-CLAIM 2</div>
          </div>

          <div className="border border-green-700 bg-green-100/40 rounded-lg p-4">
            <div className="flex items-start justify-between mb-2">
              <div className="text-stone-900 text-sm">
                Activation energy decreases with temperature
              </div>
              <div className="px-2 py-0.5 bg-green-700 text-green-100 text-xs rounded">
                Supported
              </div>
            </div>
            <div className="text-xs text-stone-600 font-mono">SUB-CLAIM 3</div>
          </div>

          <div className="border border-amber-300 bg-amber-50/50 rounded-lg p-4 relative">
            <div className="absolute -left-4 top-1/2 -translate-y-1/2 w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center text-stone-900">
              !
            </div>
            <div className="flex items-start justify-between mb-2">
              <div className="text-stone-900 text-sm">
                Phase stability maintained under doping
              </div>
              <div className="px-2 py-0.5 bg-amber-700 text-amber-100 text-xs rounded">
                Untested
              </div>
            </div>
            <div className="text-xs text-stone-600 font-mono">SUB-CLAIM 4 — WEAKEST</div>
          </div>
        </div>

        <div className="mt-6 p-4 bg-yellow-100/50 border border-yellow-700 rounded">
          <div className="text-xs text-yellow-800 mb-1 font-mono">NEXT TARGET</div>
          <div className="text-stone-900 text-sm">
            Test phase stability claim (Sub-claim 4). Critical assumption with highest uncertainty.
          </div>
        </div>
      </div>
    </div>
  );
}
