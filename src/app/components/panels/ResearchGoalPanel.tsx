function asString(v: unknown): string {
  if (typeof v === "string") return v;
  if (v == null) return "";
  return String(v);
}

function asStringArray(v: unknown): string[] {
  if (!Array.isArray(v)) return [];
  return v.map((x) => asString(x)).filter(Boolean);
}

interface ResearchGoalPanelProps {
  userGoal?: string;
  intent?: Record<string, unknown> | null;
}

export function ResearchGoalPanel({ userGoal, intent }: ResearchGoalPanelProps) {
  const domain = intent ? asString(intent.domain) : "";
  const objective = intent ? asString(intent.objective) : "";
  const entities = intent ? asStringArray(intent.entities) : [];

  const hasIntent = Boolean(domain || objective || entities.length);

  return (
    <div className="space-y-4">
      <div className="bg-yellow-50/50 border border-amber-200 rounded-lg p-6">
        <h3 className="text-sm text-stone-600 mb-3">User goal</h3>
        <p className="text-stone-900 whitespace-pre-wrap">
          {userGoal?.trim() ? userGoal : "No goal loaded. Start a new run from the home screen."}
        </p>
      </div>

      <div className="bg-yellow-50/50 border border-amber-200 rounded-lg p-6">
        <h3 className="text-sm text-stone-600 mb-4">Parsed scientific intent</h3>

        {!hasIntent ? (
          <p className="text-sm text-stone-600">Intent appears after goal parsing (included when the run is created).</p>
        ) : (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-xs text-stone-600 mb-1 font-mono">DOMAIN</div>
                <div className="text-stone-900">{domain || "—"}</div>
              </div>
              <div>
                <div className="text-xs text-stone-600 mb-1 font-mono">OBJECTIVE</div>
                <div className="text-stone-900 line-clamp-6">{objective || "—"}</div>
              </div>
            </div>

            {entities.length > 0 && (
              <div>
                <div className="text-xs text-stone-600 mb-2 font-mono">ENTITIES</div>
                <div className="flex flex-wrap gap-2">
                  {entities.map((e) => (
                    <span key={e} className="px-2 py-1 bg-amber-100 text-stone-700 rounded text-sm font-mono">
                      {e}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
