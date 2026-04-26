import { ChevronDown, Download, Home, Play, ShieldCheck } from "lucide-react";
import { motion } from "motion/react";
import { useMemo, useState } from "react";

interface HeaderProps {
  runId: string;
  experimentName: string;
  workflowState?: string;
  status: "Draft" | "Scheduled" | "Running" | "Failed" | "Completed";
  onHomeClick?: () => void;
  onAdvance?: () => void;
  onApprove?: () => void;
  onExportSelection?: (subject: "hypothesis" | "experiment" | "results", format: "json" | "pdf") => void;
  onExportDemo?: () => void;
  onDemoWalkthrough?: () => void;
  showApprove?: boolean;
  actionBusy?: boolean;
}

export function Header({
  runId,
  experimentName,
  workflowState,
  status,
  onHomeClick,
  onAdvance,
  onApprove,
  onExportSelection,
  onExportDemo,
  onDemoWalkthrough,
  showApprove,
  actionBusy,
}: HeaderProps) {
  const [exportOpen, setExportOpen] = useState(false);
  const statusColors = {
    Draft: "bg-slate-500",
    Scheduled: "bg-teal-600",
    Running: "bg-green-600",
    Failed: "bg-red-600",
    Completed: "bg-emerald-600",
  };
  const exportGroups = useMemo(
    () => [
      { id: "hypothesis", label: "Hypothesis" },
      { id: "experiment", label: "Experiment" },
      { id: "results", label: "Results" },
    ],
    [],
  );

  return (
    <header className="h-16 border-b border-amber-200 bg-yellow-50/50 flex items-center justify-between px-6 shadow-sm">
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-br from-green-600 to-emerald-700 rounded-md flex items-center justify-center overflow-hidden">
            <motion.svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              animate={{ rotateY: 360 }}
              transition={{
                duration: 8,
                repeat: Infinity,
                ease: "linear",
              }}
            >
              <path
                d="M12 2 Q 8 6 12 10 Q 16 6 12 2"
                stroke="#fff"
                strokeWidth="1.5"
                fill="none"
                opacity="0.8"
              />
              <path
                d="M12 10 Q 16 14 12 18 Q 8 14 12 10"
                stroke="#fff"
                strokeWidth="1.5"
                fill="none"
                opacity="0.8"
              />
              <path
                d="M12 18 Q 8 22 12 26"
                stroke="#fff"
                strokeWidth="1.5"
                fill="none"
                opacity="0.8"
              />
              <circle cx="12" cy="4" r="1.5" fill="#fff" opacity="0.9" />
              <circle cx="12" cy="12" r="1.5" fill="#fff" opacity="0.9" />
              <circle cx="12" cy="20" r="1.5" fill="#fff" opacity="0.9" />
            </motion.svg>
          </div>
          <h1 className="text-xl text-stone-900 tracking-tight">HelixLabs</h1>
        </div>

        <div className="h-8 w-px bg-amber-300" />

        <div className="flex flex-col">
          <div className="text-xs text-stone-600 font-mono">
            {runId}
            {workflowState ? <span className="text-stone-500"> · {workflowState}</span> : null}
          </div>
          <div className="text-sm text-stone-900 line-clamp-2">{experimentName}</div>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {onHomeClick && (
          <button
            onClick={onHomeClick}
            className="px-3 py-2 bg-green-700 hover:bg-green-800 text-white rounded flex items-center gap-2 transition-colors"
          >
            <Home className="w-4 h-4" />
          </button>
        )}

        <div className={`px-3 py-1 rounded ${statusColors[status]} text-white text-sm font-medium`}>
          {status}
        </div>

        {onAdvance && (
          <button
            type="button"
            disabled={actionBusy}
            onClick={onAdvance}
            title="Advance"
            aria-label="Advance"
            className="w-9 h-9 bg-green-700 hover:bg-green-800 disabled:opacity-50 text-white rounded flex items-center justify-center transition-colors"
          >
            <Play className="w-4 h-4" />
          </button>
        )}
        {onDemoWalkthrough && (
          <button
            type="button"
            disabled={actionBusy}
            onClick={onDemoWalkthrough}
            title="Demo Walkthrough"
            aria-label="Demo Walkthrough"
            className="w-9 h-9 bg-emerald-700 hover:bg-emerald-800 disabled:opacity-50 text-white rounded flex items-center justify-center transition-colors"
          >
            <Play className="w-4 h-4" />
          </button>
        )}

        {showApprove && onApprove && (
          <button
            type="button"
            disabled={actionBusy}
            onClick={onApprove}
            title="Approve"
            aria-label="Approve"
            className="w-9 h-9 bg-teal-700 hover:bg-teal-800 disabled:opacity-50 text-white rounded flex items-center justify-center transition-colors"
          >
            <ShieldCheck className="w-4 h-4" />
          </button>
        )}

        {onExportSelection && (
          <div className="relative">
            <button
              type="button"
              disabled={actionBusy}
              onClick={() => setExportOpen((v) => !v)}
              title="Export"
              aria-label="Export"
              className="h-9 px-3 bg-green-700 hover:bg-green-800 disabled:opacity-50 text-white rounded flex items-center justify-center gap-1.5 transition-colors"
            >
              <Download className="w-4 h-4" />
              <span className="text-xs font-medium">Export</span>
              <ChevronDown className="w-3.5 h-3.5" />
            </button>
            {exportOpen && (
              <div className="absolute right-0 mt-2 w-64 rounded-md border border-amber-200 bg-white shadow-lg z-20 p-2">
                <div className="text-[11px] font-mono text-stone-500 px-2 pb-1">Export Format</div>
                <div className="space-y-2">
                  {exportGroups.map((group) => (
                    <div key={group.id} className="rounded border border-amber-100 bg-amber-50/30 p-2">
                      <div className="text-xs text-stone-700 mb-1">{group.label}</div>
                      <div className="flex gap-2">
                        <button
                          type="button"
                          disabled={actionBusy}
                          className="flex-1 text-xs rounded bg-emerald-700 hover:bg-emerald-800 disabled:opacity-50 text-white px-2 py-1"
                          onClick={() => {
                            onExportSelection(group.id as "hypothesis" | "experiment" | "results", "json");
                            setExportOpen(false);
                          }}
                        >
                          JSON
                        </button>
                        <button
                          type="button"
                          disabled={actionBusy}
                          className="flex-1 text-xs rounded bg-teal-700 hover:bg-teal-800 disabled:opacity-50 text-white px-2 py-1"
                          onClick={() => {
                            onExportSelection(group.id as "hypothesis" | "experiment" | "results", "pdf");
                            setExportOpen(false);
                          }}
                        >
                          PDF
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
        {onExportDemo && (
          <button
            type="button"
            disabled={actionBusy}
            onClick={onExportDemo}
            title="Export Demo"
            aria-label="Export Demo"
            className="w-9 h-9 bg-teal-700 hover:bg-teal-800 disabled:opacity-50 text-white rounded flex items-center justify-center transition-colors"
          >
            <Download className="w-4 h-4" />
          </button>
        )}
      </div>
    </header>
  );
}
