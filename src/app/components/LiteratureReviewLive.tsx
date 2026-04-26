import { useEffect, useState } from "react";
import { motion } from "motion/react";
import { ArrowRight, Calendar, CheckCircle2, Loader2, Users, X, XCircle } from "lucide-react";

interface LiteratureReviewProps {
  experiment: string;
  /** When set, loads that run instead of creating a new one (single session). */
  runId?: string | null;
  onProceedToDashboard: () => void;
}

interface Study {
  id: string;
  title: string;
  authors: string;
  year: number | null;
  relevancy: number;
  similarity: number;
  exists: boolean;
  citation: string | null;
  methodology: string;
  findings: string;
  limitations: string;
  equipmentEstimate: string;
  fundingEstimate: string;
}

export function LiteratureReviewLive({ experiment, runId: existingRunId, onProceedToDashboard }: LiteratureReviewProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [studies, setStudies] = useState<Study[]>([]);
  const [selectedStudy, setSelectedStudy] = useState<Study | null>(null);
  const [noveltyScore, setNoveltyScore] = useState("0.0");

  useEffect(() => {
    const load = async () => {
      setIsLoading(true);
      setErrorMessage(null);
      setSelectedStudy(null);

      try {
        const apiBase = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "http://127.0.0.1:8000";
        let runId = existingRunId?.trim() || "";

        if (!runId) {
          const createRes = await fetch(`${apiBase}/api/runs`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_goal: experiment }),
          });
          if (!createRes.ok) {
            throw new Error(`Unable to create run (${createRes.status})`);
          }

          const createData = await createRes.json();
          runId = String(createData?.run_id ?? "");
          if (!runId) {
            throw new Error("Run ID missing from API");
          }
        }

        const runRes = await fetch(`${apiBase}/api/runs/${encodeURIComponent(runId)}`);
        if (!runRes.ok) {
          throw new Error(`Unable to fetch run (${runRes.status})`);
        }

        const runData = await runRes.json();
        const intake = runData?.run?.pipeline?.intake ?? {};
        const rawStudies = Array.isArray(intake?.literature?.studies) ? intake.literature.studies : [];
        const mapped: Study[] = rawStudies.map((study: any, idx: number) => ({
          id: String(study?.doi ?? `${runId}-${idx}`),
          title: String(study?.title ?? "Untitled"),
          authors: String(study?.authors ?? "Unknown"),
          year: typeof study?.year === "number" ? study.year : null,
          relevancy: Number(study?.relevance ?? 0),
          similarity: Number(study?.similarity ?? study?.relevance ?? 0),
          exists: Boolean(study?.exists ?? true),
          citation: typeof study?.doi === "string" ? `DOI: ${study.doi}` : null,
          methodology: study?.abstract
            ? String(study.abstract).slice(0, 260)
            : String(study?.methodology ?? "Abstract not available from provider."),
          findings: String(study?.findings ?? "Retrieved from indexed literature metadata and ranked by relevance."),
          limitations: String(study?.limitations ?? "Metadata-level synthesis; manual full-text review recommended."),
          equipmentEstimate: String(study?.equipment_estimate ?? "Estimated equipment not provided."),
          fundingEstimate: String(study?.funding_estimate ?? "Estimated funding not provided."),
        }));

        setStudies(mapped);
        const score = Number(intake?.prior_work?.novelty_score);
        setNoveltyScore(Number.isFinite(score) ? score.toFixed(1) : "0.0");
      } catch (error) {
        setStudies([]);
        setNoveltyScore("0.0");
        if (error instanceof TypeError) {
          setErrorMessage("Failed to fetch from API. Make sure backend is running on http://127.0.0.1:8000.");
        } else {
          setErrorMessage(error instanceof Error ? error.message : "Failed to load studies");
        }
      } finally {
        setIsLoading(false);
      }
    };

    if (!experiment.trim()) {
      setStudies([]);
      setNoveltyScore("0.0");
      setIsLoading(false);
      return;
    }

    void load();
  }, [experiment, existingRunId]);

  const existingStudies = studies.filter((s) => s.exists);
  const avgRelevancy =
    studies.length > 0
      ? ((studies.reduce((sum, s) => sum + s.relevancy, 0) / studies.length) * 100).toFixed(0)
      : "0";

  return (
    <div className="w-full h-full bg-gradient-to-br from-amber-50 via-yellow-50 to-orange-50 relative flex flex-col">
      <div className="relative z-10 w-full flex-1 flex flex-col min-h-0">
        {!isLoading && (
          <div className="p-8 border-b border-amber-200">
            <div className="bg-yellow-50/50 rounded-2xl p-6 border border-amber-200 shadow-lg">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-3xl font-light text-stone-900 mb-2">Literature Review</h2>
                  <p className="text-stone-700">
                    Analyzing prior work for: <span className="text-green-700 font-medium">{experiment}</span>
                  </p>
                </div>
                <div className="flex gap-4">
                  <div className="px-4 py-3 bg-green-50 border border-green-200 rounded-xl shadow-sm">
                    <div className="text-xs text-green-700 mb-1 font-medium">Studies Found</div>
                    <div className="text-2xl text-stone-900 font-light">{existingStudies.length}/{studies.length}</div>
                  </div>
                  <div className="px-4 py-3 bg-emerald-50 border border-emerald-200 rounded-xl shadow-sm">
                    <div className="text-xs text-emerald-700 mb-1 font-medium">Novelty Score</div>
                    <div className="text-2xl text-stone-900 font-light">{noveltyScore}/10</div>
                  </div>
                  <div className="px-4 py-3 bg-teal-50 border border-teal-200 rounded-xl shadow-sm">
                    <div className="text-xs text-teal-700 mb-1 font-medium">Avg Relevancy</div>
                    <div className="text-2xl text-stone-900 font-light">{avgRelevancy}%</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="flex-1 flex min-h-0">
          {isLoading ? (
            <div className="flex-1 flex flex-col items-center justify-center min-h-0">
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center">
                <Loader2 className="w-12 h-12 text-green-600 animate-spin mx-auto mb-4" />
                <div className="text-xl text-stone-900 mb-2">Searching Literature</div>
                <div className="text-stone-700">Querying and ranking real indexed studies...</div>
              </motion.div>
            </div>
          ) : (
            <div className="flex-1 overflow-y-auto p-8">
              {errorMessage && (
                <div className="max-w-4xl mx-auto mb-4 rounded-lg border border-red-300 bg-red-100/40 px-4 py-3 text-sm text-red-900">
                  {errorMessage}
                </div>
              )}
              <div className="max-w-4xl mx-auto space-y-4">
                {studies.map((study, index) => (
                  <motion.div
                    key={study.id}
                    initial={{ opacity: 0, y: 20, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    transition={{ delay: index * 0.08, type: "spring", stiffness: 100 }}
                    onClick={() => setSelectedStudy(study)}
                    className="group bg-yellow-50/30 border border-amber-200 rounded-2xl p-6 hover:border-green-400 hover:shadow-lg cursor-pointer transition-all"
                  >
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0 mt-1">
                        {study.exists ? (
                          <div className="w-10 h-10 rounded-full bg-green-100 border border-green-300 flex items-center justify-center">
                            <CheckCircle2 className="w-5 h-5 text-green-700" />
                          </div>
                        ) : (
                          <div className="w-10 h-10 rounded-full bg-amber-100 border border-amber-300 flex items-center justify-center">
                            <XCircle className="w-5 h-5 text-amber-700" />
                          </div>
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="text-stone-900 font-medium mb-3 leading-tight group-hover:text-green-800 transition-colors">
                          {study.title}
                        </h3>
                        <div className="flex items-center gap-4 text-sm text-stone-700 mb-4">
                          <div className="flex items-center gap-2"><Users className="w-4 h-4" /><span>{study.authors}</span></div>
                          <div className="flex items-center gap-2"><Calendar className="w-4 h-4" /><span>{study.year ?? "N/A"}</span></div>
                        </div>
                        <div className="flex items-center gap-3 flex-wrap">
                          <div className="px-3 py-1.5 bg-teal-50 border border-teal-200 rounded-full text-xs text-teal-700 font-medium">
                            {(study.relevancy * 100).toFixed(1)}% relevant
                          </div>
                          <div className="px-3 py-1.5 bg-emerald-50 border border-emerald-200 rounded-full text-xs text-emerald-700 font-medium">
                            {(study.similarity * 100).toFixed(1)}% similar
                          </div>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          {selectedStudy && (
            <motion.div
              initial={{ x: 400, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              className="w-[500px] bg-orange-50/30 border-l border-amber-200 overflow-y-auto shadow-xl"
            >
              <div className="p-6">
                <div className="flex items-start justify-between mb-6">
                  <div>
                    <div className="text-sm text-stone-800 font-medium">{selectedStudy.exists ? "Existing Study" : "Research Gap"}</div>
                    <div className="text-xs text-stone-600">{selectedStudy.citation ?? "No citation available"}</div>
                  </div>
                  <button onClick={() => setSelectedStudy(null)} className="text-stone-600 hover:text-stone-900 transition-colors">
                    <X className="w-5 h-5" />
                  </button>
                </div>
                <h3 className="text-xl text-stone-900 font-medium mb-4 leading-tight">{selectedStudy.title}</h3>
                <div className="space-y-4">
                  <div className="bg-yellow-50/50 border border-amber-200 rounded-xl p-4">
                    <div className="text-sm text-stone-800 mb-2 font-medium">Methodology/Abstract</div>
                    <div className="text-sm text-stone-700 leading-relaxed">{selectedStudy.methodology}</div>
                  </div>
                  <div className="bg-yellow-50/50 border border-amber-200 rounded-xl p-4">
                    <div className="text-sm text-stone-800 mb-2 font-medium">Findings</div>
                    <div className="text-sm text-stone-700 leading-relaxed">{selectedStudy.findings}</div>
                  </div>
                  <div className="bg-yellow-50/50 border border-amber-200 rounded-xl p-4">
                    <div className="text-sm text-stone-800 mb-2 font-medium">Limitations</div>
                    <div className="text-sm text-stone-700 leading-relaxed">{selectedStudy.limitations}</div>
                  </div>
                  <div className="bg-yellow-50/50 border border-amber-200 rounded-xl p-4">
                    <div className="text-sm text-stone-800 mb-2 font-medium">Equipment Estimate</div>
                    <div className="text-sm text-stone-700 leading-relaxed">{selectedStudy.equipmentEstimate}</div>
                  </div>
                  <div className="bg-yellow-50/50 border border-amber-200 rounded-xl p-4">
                    <div className="text-sm text-stone-800 mb-2 font-medium">Funding Estimate</div>
                    <div className="text-sm text-stone-700 leading-relaxed">{selectedStudy.fundingEstimate}</div>
                  </div>
                </div>
                <div className="mt-8">
                  <motion.button
                    onClick={onProceedToDashboard}
                    className="w-full px-6 py-4 bg-green-700 hover:bg-green-800 text-white rounded-xl flex items-center justify-center gap-2 transition-all shadow-lg font-medium"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <ArrowRight className="w-5 h-5" />
                    Proceed to Dashboard
                  </motion.button>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
