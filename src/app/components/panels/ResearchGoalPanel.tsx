export function ResearchGoalPanel() {
  return (
    <div className="space-y-4">
      <div className="bg-yellow-50/50 border border-amber-200 rounded-lg p-6">
        <h3 className="text-sm text-stone-600 mb-3">User Input</h3>
        <p className="text-stone-900">
          Investigate the effect of transition metal doping on the ionic conductivity
          of lithium lanthanum titanate solid electrolytes at varying temperatures
        </p>
      </div>

      <div className="bg-yellow-50/50 border border-amber-200 rounded-lg p-6">
        <h3 className="text-sm text-stone-600 mb-4">Parsed Scientific Intent</h3>

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-xs text-stone-600 mb-1 font-mono">DOMAIN</div>
              <div className="text-stone-900">Materials Science / Solid-State Chemistry</div>
            </div>
            <div>
              <div className="text-xs text-stone-600 mb-1 font-mono">OBJECTIVE</div>
              <div className="text-stone-900">Optimize ionic conductivity</div>
            </div>
          </div>

          <div>
            <div className="text-xs text-stone-600 mb-2 font-mono">CONSTRAINTS</div>
            <div className="flex flex-wrap gap-2">
              <span className="px-2 py-1 bg-amber-100 text-stone-700 rounded text-sm font-mono">
                Temperature: 25-300°C
              </span>
              <span className="px-2 py-1 bg-amber-100 text-stone-700 rounded text-sm font-mono">
                Dopant concentration: 0.1-10 mol%
              </span>
              <span className="px-2 py-1 bg-amber-100 text-stone-700 rounded text-sm font-mono">
                Base material: Li₇La₃Zr₂O₁₂
              </span>
            </div>
          </div>

          <div>
            <div className="text-xs text-stone-600 mb-2 font-mono">METRICS</div>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-600 rounded-full" />
                <span className="text-stone-700 font-mono text-sm">σ_ionic (S/cm)</span>
                <span className="text-stone-600">— Primary</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-blue-600 rounded-full" />
                <span className="text-stone-700 font-mono text-sm">E_activation (eV)</span>
                <span className="text-stone-600">— Secondary</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-blue-600 rounded-full" />
                <span className="text-stone-700 font-mono text-sm">Phase purity (%)</span>
                <span className="text-stone-600">— Secondary</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
