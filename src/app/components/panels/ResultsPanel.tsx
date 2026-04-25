import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

export function ResultsPanel() {
  const conductivityData = [
    { temp: 25, observed: 3.8e-4, baseline: 2.4e-4 },
    { temp: 50, observed: 5.2e-4, baseline: 3.1e-4 },
    { temp: 100, observed: 8.9e-4, baseline: 5.6e-4 },
    { temp: 150, observed: 1.4e-3, baseline: 9.2e-4 },
    { temp: 200, observed: 2.1e-3, baseline: 1.5e-3 },
    { temp: 250, observed: 3.2e-3, baseline: 2.3e-3 },
    { temp: 300, observed: 4.6e-3, baseline: 3.4e-3 },
  ];

  return (
    <div className="space-y-4">
      <div className="bg-yellow-50/50 border border-amber-200 rounded-lg p-6">
        <h3 className="text-sm text-stone-600 mb-4">Observed Results</h3>

        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="p-4 bg-green-100/30 border border-green-700 rounded">
            <div className="text-xs text-green-800 mb-1 font-mono">σ @ 25°C</div>
            <div className="text-2xl text-stone-900">3.8×10⁻⁴</div>
            <div className="text-xs text-stone-600">S/cm (58% above baseline)</div>
          </div>

          <div className="p-4 bg-green-100/30 border border-green-700 rounded">
            <div className="text-xs text-green-800 mb-1 font-mono">E_activation</div>
            <div className="text-2xl text-stone-900">0.32</div>
            <div className="text-xs text-stone-600">eV (12% reduction)</div>
          </div>

          <div className="p-4 bg-green-100/30 border border-green-700 rounded">
            <div className="text-xs text-green-800 mb-1 font-mono">Phase purity</div>
            <div className="text-2xl text-stone-900">97.2</div>
            <div className="text-xs text-stone-600">% (target: &gt;95%)</div>
          </div>
        </div>

        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={conductivityData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#D1D5DB" />
              <XAxis
                dataKey="temp"
                stroke="#57534E"
                label={{ value: 'Temperature (°C)', position: 'insideBottom', offset: -5, fill: '#57534E' }}
              />
              <YAxis
                stroke="#57534E"
                tickFormatter={(value) => value.toExponential(1)}
                label={{ value: 'σ (S/cm)', angle: -90, position: 'insideLeft', fill: '#57534E' }}
              />
              <Tooltip
                contentStyle={{ backgroundColor: '#FEF3C7', border: '1px solid #F59E0B' }}
                labelStyle={{ color: '#57534E' }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="observed"
                stroke="#10B981"
                strokeWidth={2}
                name="Fe-doped LLZO"
              />
              <Line
                type="monotone"
                dataKey="baseline"
                stroke="#78716C"
                strokeWidth={2}
                strokeDasharray="5 5"
                name="Baseline (undoped)"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-yellow-50/50 border border-amber-200 rounded-lg p-6">
        <h3 className="text-sm text-stone-600 mb-4">Prior Evidence</h3>

        <div className="grid grid-cols-2 gap-4">
          <div className="p-3 bg-amber-50/50 rounded">
            <div className="text-xs text-stone-600 mb-1 font-mono">RUN #1247 (Al-doped)</div>
            <div className="text-stone-900">σ @ 25°C: 2.4×10⁻⁴ S/cm</div>
          </div>
          <div className="p-3 bg-amber-50/50 rounded">
            <div className="text-xs text-stone-600 mb-1 font-mono">RUN #1289 (Ta-doped)</div>
            <div className="text-stone-900">σ @ 25°C: 3.1×10⁻⁴ S/cm</div>
          </div>
        </div>
      </div>

      <div className="bg-yellow-50/50 border border-amber-200 rounded-lg p-6">
        <h3 className="text-sm text-stone-600 mb-4">Model Inference</h3>

        <div className="space-y-3">
          <div className="p-4 bg-blue-100/40 border border-blue-700 rounded">
            <div className="text-sm text-stone-900 mb-2">
              Fe²⁺ doping creates oxygen vacancies, increasing Li⁺ mobility
            </div>
            <div className="flex items-center gap-4 text-xs text-stone-600">
              <span>Confidence: 87%</span>
              <span>Supporting evidence: 3 studies</span>
            </div>
          </div>

          <div className="p-4 bg-blue-100/40 border border-blue-700 rounded">
            <div className="text-sm text-stone-900 mb-2">
              Optimal Fe concentration predicted at 3-5 mol%
            </div>
            <div className="flex items-center gap-4 text-xs text-stone-600">
              <span>Confidence: 72%</span>
              <span>Based on: defect chemistry model</span>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-yellow-50/50 border border-amber-200 rounded-lg p-6">
        <h3 className="text-sm text-stone-600 mb-4">Uncertainty Analysis</h3>

        <div className="space-y-2">
          <div className="flex items-center justify-between p-2 bg-amber-50/50 rounded">
            <span className="text-sm text-stone-900">Measurement precision</span>
            <span className="text-sm text-stone-600">±8%</span>
          </div>
          <div className="flex items-center justify-between p-2 bg-amber-50/50 rounded">
            <span className="text-sm text-stone-900">Sample-to-sample variation</span>
            <span className="text-sm text-stone-600">±12%</span>
          </div>
          <div className="flex items-center justify-between p-2 bg-amber-50/50 rounded">
            <span className="text-sm text-stone-900">Model prediction error</span>
            <span className="text-sm text-stone-600">±18%</span>
          </div>
        </div>
      </div>
    </div>
  );
}
