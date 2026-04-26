import { Download, Home, Play, ShieldCheck } from "lucide-react";
import { motion } from "motion/react";

interface HeaderProps {
  runId: string;
  experimentName: string;
  workflowState?: string;
  status: "Draft" | "Scheduled" | "Running" | "Failed" | "Completed";
  onHomeClick?: () => void;
  onAdvance?: () => void;
  onApprove?: () => void;
  onExportReport?: () => void;
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
  onExportReport,
  showApprove,
  actionBusy,
}: HeaderProps) {
  const statusColors = {
    Draft: "bg-slate-500",
    Scheduled: "bg-teal-600",
    Running: "bg-green-600",
    Failed: "bg-red-600",
    Completed: "bg-emerald-600",
  };

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
            className="px-4 py-2 bg-green-700 hover:bg-green-800 disabled:opacity-50 text-white rounded flex items-center gap-2 transition-colors"
          >
            <Play className="w-4 h-4" />
            Advance
          </button>
        )}

        {showApprove && onApprove && (
          <button
            type="button"
            disabled={actionBusy}
            onClick={onApprove}
            className="px-4 py-2 bg-teal-700 hover:bg-teal-800 disabled:opacity-50 text-white rounded flex items-center gap-2 transition-colors"
          >
            <ShieldCheck className="w-4 h-4" />
            Approve
          </button>
        )}

        {onExportReport && (
          <button
            type="button"
            disabled={actionBusy}
            onClick={onExportReport}
            className="px-4 py-2 bg-green-700 hover:bg-green-800 disabled:opacity-50 text-white rounded flex items-center gap-2 transition-colors"
          >
            <Download className="w-4 h-4" />
            Export Report
          </button>
        )}
      </div>
    </header>
  );
}
