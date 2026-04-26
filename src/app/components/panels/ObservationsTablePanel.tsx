interface ObservationsTablePanelProps {
  observations?: Array<Record<string, unknown>> | null;
}

function valueToString(v: unknown): string {
  if (v == null) return "";
  if (typeof v === "number") return Number.isFinite(v) ? String(v) : "";
  if (typeof v === "boolean") return v ? "true" : "false";
  if (typeof v === "string") return v;
  return JSON.stringify(v);
}

export function ObservationsTablePanel({ observations }: ObservationsTablePanelProps) {
  const rows = Array.isArray(observations) ? observations : [];
  if (rows.length === 0) {
    return (
      <div className="rounded-lg border border-amber-200 bg-yellow-50/50 p-4 text-sm text-stone-600">
        No observations yet. Run execution stages to materialize measured rows.
      </div>
    );
  }

  const keys = Array.from(
    rows.reduce((set, row) => {
      Object.keys(row).forEach((k) => set.add(k));
      return set;
    }, new Set<string>()),
  );
  const preview = rows.slice(0, 120);

  return (
    <div className="bg-yellow-50/50 border border-amber-200 rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm text-stone-600">Observations</h3>
        <div className="text-xs text-stone-500">{rows.length} rows</div>
      </div>

      <div className="overflow-auto max-h-[360px] rounded border border-amber-200 bg-white/80">
        <table className="min-w-full text-xs">
          <thead className="sticky top-0 bg-amber-100/70">
            <tr>
              {keys.map((k) => (
                <th key={k} className="text-left px-3 py-2 font-mono text-stone-700 whitespace-nowrap">
                  {k}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {preview.map((row, i) => (
              <tr key={i} className="border-t border-amber-100">
                {keys.map((k) => (
                  <td key={k} className="px-3 py-2 text-stone-800 whitespace-nowrap">
                    {valueToString(row[k])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {rows.length > preview.length && (
        <p className="mt-2 text-xs text-stone-500">Showing first {preview.length} rows for readability.</p>
      )}
    </div>
  );
}
