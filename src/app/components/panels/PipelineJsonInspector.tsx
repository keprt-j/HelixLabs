import { Check, Clipboard, ChevronDown, ChevronRight } from "lucide-react";
import React, { useMemo, useState } from "react";

interface PipelineJsonInspectorProps {
  title: string;
  summary?: string | null;
  generatedAt?: string | null;
  data: Record<string, unknown>;
}

export function PipelineJsonInspector({ title, summary, generatedAt, data }: PipelineJsonInspectorProps) {
  const [open, setOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const json = useMemo(() => JSON.stringify(data ?? {}, null, 2), [data]);
  const isEmpty = !data || Object.keys(data).length === 0;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(json);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1200);
    } catch {
      setCopied(false);
    }
  };

  return (
    <div className="mt-6 rounded-lg border border-blue-200 bg-blue-50/40 p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-xs font-mono text-blue-700 uppercase tracking-wide">{title}</div>
          <p className="mt-2 text-sm text-blue-950">
            {summary?.trim() ? summary : isEmpty ? "No pipeline JSON is available yet." : "Pipeline JSON is available for inspection."}
          </p>
          {generatedAt ? <div className="mt-2 text-[11px] text-blue-700">summary generated: {new Date(generatedAt).toLocaleString()}</div> : null}
        </div>
        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          className="shrink-0 rounded bg-blue-700 px-3 py-2 text-xs text-white hover:bg-blue-800 inline-flex items-center gap-1"
        >
          {open ? <ChevronDown className="h-3.5 w-3.5" /> : <ChevronRight className="h-3.5 w-3.5" />}
          {open ? "Hide JSON" : "View JSON"}
        </button>
      </div>

      {open ? (
        <div className="mt-4">
          <div className="mb-2 flex justify-end">
            <button
              type="button"
              onClick={() => void handleCopy()}
              className="rounded border border-blue-300 bg-white/80 px-2 py-1 text-xs text-blue-900 hover:bg-white inline-flex items-center gap-1"
            >
              {copied ? <Check className="h-3.5 w-3.5" /> : <Clipboard className="h-3.5 w-3.5" />}
              {copied ? "Copied" : "Copy"}
            </button>
          </div>
          <pre className="max-h-96 overflow-auto rounded border border-blue-200 bg-white/80 p-3 text-xs leading-relaxed text-stone-900">
            {json}
          </pre>
        </div>
      ) : null}
    </div>
  );
}
