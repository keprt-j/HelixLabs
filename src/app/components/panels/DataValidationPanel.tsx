import { CheckCircle2, AlertTriangle, ArrowRight } from "lucide-react";

export function DataValidationPanel() {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-yellow-50/50 border border-amber-200 rounded-lg p-6">
          <h3 className="text-sm text-stone-600 mb-4">Expected Schema</h3>

          <div className="space-y-2 font-mono text-sm">
            <div className="p-2 bg-amber-50/50 rounded">
              <span className="text-blue-600">sample_id</span>
              <span className="text-stone-600">: string</span>
            </div>
            <div className="p-2 bg-amber-50/50 rounded">
              <span className="text-blue-600">temperature</span>
              <span className="text-stone-600">: float (°C)</span>
            </div>
            <div className="p-2 bg-amber-50/50 rounded">
              <span className="text-blue-600">conductivity</span>
              <span className="text-stone-600">: float (S/cm)</span>
            </div>
            <div className="p-2 bg-amber-50/50 rounded">
              <span className="text-blue-600">activation_energy</span>
              <span className="text-stone-600">: float (eV)</span>
            </div>
            <div className="p-2 bg-amber-50/50 rounded">
              <span className="text-blue-600">phase_purity</span>
              <span className="text-stone-600">: float (%)</span>
            </div>
          </div>
        </div>

        <div className="bg-yellow-50/50 border border-amber-200 rounded-lg p-6">
          <h3 className="text-sm text-stone-600 mb-4">Actual Data</h3>

          <div className="space-y-2 font-mono text-sm">
            <div className="p-2 bg-amber-50/50 rounded">
              <span className="text-blue-600">sample_id</span>
              <span className="text-green-600">: string ✓</span>
            </div>
            <div className="p-2 bg-amber-50/50 rounded">
              <span className="text-blue-600">temp_celsius</span>
              <span className="text-yellow-700">: float ⚠</span>
            </div>
            <div className="p-2 bg-amber-50/50 rounded">
              <span className="text-blue-600">sigma_ionic</span>
              <span className="text-yellow-700">: float ⚠</span>
            </div>
            <div className="p-2 bg-amber-50/50 rounded">
              <span className="text-blue-600">e_hull</span>
              <span className="text-yellow-700">: float ⚠</span>
            </div>
            <div className="p-2 bg-amber-50/50 rounded">
              <span className="text-blue-600">phase_purity</span>
              <span className="text-green-600">: float ✓</span>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-yellow-50/50 border border-amber-200 rounded-lg p-6">
        <h3 className="text-sm text-stone-600 mb-4">Detected Issues & Auto-Repairs</h3>

        <div className="space-y-3">
          <div className="flex items-start gap-3 p-3 bg-yellow-100/40 border border-yellow-700 rounded">
            <AlertTriangle className="w-4 h-4 text-yellow-700 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <div className="flex items-center gap-2 text-sm mb-2">
                <span className="font-mono text-stone-900">temp_celsius</span>
                <ArrowRight className="w-3 h-3 text-stone-600" />
                <span className="font-mono text-stone-900">temperature</span>
              </div>
              <div className="text-xs text-stone-600">
                Column name mismatch. Auto-mapped to expected schema.
              </div>
            </div>
            <CheckCircle2 className="w-4 h-4 text-green-600 flex-shrink-0" />
          </div>

          <div className="flex items-start gap-3 p-3 bg-yellow-100/40 border border-yellow-700 rounded">
            <AlertTriangle className="w-4 h-4 text-yellow-700 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <div className="flex items-center gap-2 text-sm mb-2">
                <span className="font-mono text-stone-900">sigma_ionic</span>
                <ArrowRight className="w-3 h-3 text-stone-600" />
                <span className="font-mono text-stone-900">conductivity</span>
              </div>
              <div className="text-xs text-stone-600">
                Column name mismatch. Auto-mapped to expected schema.
              </div>
            </div>
            <CheckCircle2 className="w-4 h-4 text-green-600 flex-shrink-0" />
          </div>

          <div className="flex items-start gap-3 p-3 bg-yellow-100/40 border border-yellow-700 rounded">
            <AlertTriangle className="w-4 h-4 text-yellow-700 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <div className="flex items-center gap-2 text-sm mb-2">
                <span className="font-mono text-stone-900">e_hull</span>
                <ArrowRight className="w-3 h-3 text-stone-600" />
                <span className="font-mono text-stone-900">activation_energy</span>
              </div>
              <div className="text-xs text-stone-600">
                Semantic mapping applied. Verified units match (eV).
              </div>
            </div>
            <CheckCircle2 className="w-4 h-4 text-green-600 flex-shrink-0" />
          </div>
        </div>
      </div>

      <div className="bg-green-100/30 border border-green-700 rounded-lg p-4">
        <div className="flex items-center gap-3">
          <CheckCircle2 className="w-5 h-5 text-green-700 flex-shrink-0" />
          <div>
            <div className="text-sm text-green-800 mb-1">Validation Complete</div>
            <div className="text-sm text-stone-900">
              35 records validated. All issues auto-repaired. Data ready for analysis.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
