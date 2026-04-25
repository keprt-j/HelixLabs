import { XCircle, RefreshCw, SkipForward, RotateCcw, CheckCircle2 } from "lucide-react";

export function FailureRecoveryPanel() {
  return (
    <div className="space-y-4">
      <div className="bg-red-100/40 border border-red-700 rounded-lg p-6">
        <div className="flex items-start gap-3 mb-4">
          <XCircle className="w-5 h-5 text-red-700 mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <h3 className="text-sm text-red-800 mb-2">Failure Detected</h3>
            <div className="text-stone-900 mb-2">
              XRD analysis failed: insufficient peak intensity
            </div>
            <div className="text-sm text-stone-700">
              Step 8 of 9 • 2026-04-25 14:32:18
            </div>
          </div>
        </div>

        <div className="bg-stone-900 rounded p-4 font-mono text-xs">
          <div className="text-red-400">[14:32:18] ERROR: XRD peak intensity below threshold</div>
          <div className="text-stone-400">[14:32:18] DETAIL: Max intensity = 142 counts (min = 500)</div>
          <div className="text-stone-400">[14:32:18] CAUSE: Sample surface roughness or misalignment</div>
        </div>
      </div>

      <div className="bg-yellow-50/50 border border-amber-200 rounded-lg p-6">
        <h3 className="text-sm text-stone-600 mb-4">Recovery Options</h3>

        <div className="space-y-3">
          <button className="w-full text-left p-4 bg-amber-50/50 hover:bg-amber-100 border border-amber-200 hover:border-blue-600 rounded transition-colors group">
            <div className="flex items-start gap-3">
              <RefreshCw className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <div className="text-stone-900 mb-1 group-hover:text-blue-700">Retry step with sample re-polishing</div>
                <div className="text-sm text-stone-600">
                  Polish sample surface and rerun XRD analysis
                </div>
                <div className="text-xs text-stone-600 mt-2">
                  Estimated time: +45 min
                </div>
              </div>
            </div>
          </button>

          <button className="w-full text-left p-4 bg-amber-50/50 hover:bg-amber-100 border border-amber-200 hover:border-yellow-700 rounded transition-colors group">
            <div className="flex items-start gap-3">
              <SkipForward className="w-5 h-5 text-yellow-700 mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <div className="text-stone-900 mb-1 group-hover:text-yellow-800">Skip XRD, proceed to impedance</div>
                <div className="text-sm text-stone-600">
                  Continue with remaining measurements, flag sample for manual review
                </div>
                <div className="text-xs text-stone-600 mt-2">
                  Estimated time: +0 min (phase validation incomplete)
                </div>
              </div>
            </div>
          </button>

          <button className="w-full text-left p-4 bg-amber-50/50 hover:bg-amber-100 border border-amber-200 hover:border-red-700 rounded transition-colors group">
            <div className="flex items-start gap-3">
              <RotateCcw className="w-5 h-5 text-red-700 mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <div className="text-stone-900 mb-1 group-hover:text-red-800">Rerun full experiment</div>
                <div className="text-sm text-stone-600">
                  Abort current run and start from synthesis step
                </div>
                <div className="text-xs text-stone-600 mt-2">
                  Estimated time: +28 hours
                </div>
              </div>
            </div>
          </button>
        </div>
      </div>

      <div className="bg-green-100/30 border border-green-700 rounded-lg p-6">
        <div className="flex items-start gap-3">
          <CheckCircle2 className="w-5 h-5 text-green-700 mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <h3 className="text-sm text-green-800 mb-2">Recovery Applied</h3>
            <div className="text-stone-900 mb-2">
              Selected: Retry step with sample re-polishing
            </div>
            <div className="text-sm text-stone-700">
              Recovery initiated at 2026-04-25 14:35:02
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
