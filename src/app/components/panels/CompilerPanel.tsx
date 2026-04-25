import { AlertTriangle } from "lucide-react";

export function CompilerPanel() {
  return (
    <div className="space-y-4">
      <div className="bg-yellow-50/50 border border-amber-200 rounded-lg p-6">
        <h3 className="text-sm text-stone-600 mb-4">Experiment Summary</h3>

        <div className="space-y-6">
          <div>
            <div className="text-xs text-stone-600 mb-2 font-mono">VARIABLES</div>
            <div className="space-y-2">
              <div className="flex items-center justify-between p-2 bg-amber-50/50 rounded">
                <span className="text-stone-700 font-mono text-sm">dopant_type</span>
                <span className="text-stone-600">Fe</span>
              </div>
              <div className="flex items-center justify-between p-2 bg-amber-50/50 rounded">
                <span className="text-stone-700 font-mono text-sm">dopant_concentration</span>
                <span className="text-stone-600">[0.1, 0.5, 1.0, 3.0, 5.0] mol%</span>
              </div>
              <div className="flex items-center justify-between p-2 bg-amber-50/50 rounded">
                <span className="text-stone-700 font-mono text-sm">temperature</span>
                <span className="text-stone-600">[25, 50, 100, 150, 200, 250, 300] °C</span>
              </div>
            </div>
          </div>

          <div>
            <div className="text-xs text-stone-600 mb-2 font-mono">CONTROLS</div>
            <div className="space-y-2">
              <div className="flex items-center justify-between p-2 bg-amber-50/50 rounded">
                <span className="text-stone-700 text-sm">Undoped LLZO baseline</span>
                <span className="text-green-600 text-xs">✓ Included</span>
              </div>
              <div className="flex items-center justify-between p-2 bg-amber-50/50 rounded">
                <span className="text-stone-700 text-sm">Reference electrode</span>
                <span className="text-green-600 text-xs">✓ Included</span>
              </div>
              <div className="flex items-center justify-between p-2 bg-amber-50/50 rounded">
                <span className="text-stone-700 text-sm">Humidity control</span>
                <span className="text-green-600 text-xs">✓ Included</span>
              </div>
            </div>
          </div>

          <div>
            <div className="text-xs text-stone-600 mb-2 font-mono">SUCCESS METRICS</div>
            <div className="space-y-2">
              <div className="p-2 bg-amber-50/50 rounded">
                <div className="text-stone-700 text-sm mb-1">Primary: σ_ionic &gt; 5×10⁻⁴ S/cm</div>
                <div className="text-xs text-stone-600 font-mono">Target improvement: 2× baseline</div>
              </div>
              <div className="p-2 bg-amber-50/50 rounded">
                <div className="text-stone-700 text-sm mb-1">Secondary: Phase purity &gt; 95%</div>
                <div className="text-xs text-stone-600 font-mono">XRD validation required</div>
              </div>
            </div>
          </div>

          <div>
            <div className="text-xs text-stone-600 mb-2 font-mono">REQUIRED RESOURCES</div>
            <div className="grid grid-cols-2 gap-2">
              <div className="p-2 bg-amber-50/50 rounded text-sm text-stone-700">
                Tube Furnace A
              </div>
              <div className="p-2 bg-amber-50/50 rounded text-sm text-stone-700">
                XRD Instrument
              </div>
              <div className="p-2 bg-amber-50/50 rounded text-sm text-stone-700">
                Impedance Analyzer
              </div>
              <div className="p-2 bg-amber-50/50 rounded text-sm text-stone-700">
                Glove Box #3
              </div>
            </div>
          </div>

          <div>
            <div className="text-xs text-stone-600 mb-2 font-mono">EXPECTED OUTPUTS</div>
            <div className="space-y-1 text-sm text-stone-700">
              <div>• Conductivity data: 35 measurement points</div>
              <div>• XRD patterns: 5 samples</div>
              <div>• SEM images: 5 samples</div>
              <div>• Nyquist plots: 35 files</div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-yellow-100/50 border border-yellow-700 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-yellow-700 mt-0.5 flex-shrink-0" />
          <div>
            <div className="text-sm text-yellow-800 mb-2">Compiler Warnings (1)</div>
            <div className="text-sm text-stone-700">
              Temperature sweep above 250°C may exceed furnace controller spec. Verify max operating temp before scheduling.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
