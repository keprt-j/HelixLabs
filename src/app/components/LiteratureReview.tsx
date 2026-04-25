import { useState, useEffect } from "react";
import { motion } from "motion/react";
import { ArrowRight, X, CheckCircle2, XCircle, Calendar, Users, Loader2 } from "lucide-react";

interface Study {
  id: number;
  title: string;
  authors: string;
  year: number;
  relevancy: number;
  exists: boolean;
  similarity: number;
  citation: string;
  methodology: string;
  findings: string;
  limitations: string;
  equipment: string;
  funding: string;
  position: number;
}

interface LiteratureReviewProps {
  experiment: string;
  onProceedToDashboard: () => void;
}

const generateMockStudies = (experiment: string): Study[] => {
  const allStudies = [
    {
      id: 1,
      title: "Enhanced Ionic Conductivity in Transition Metal Doped Solid Electrolytes",
      authors: "Zhang, L., Chen, M., Wang, K.",
      year: 2024,
      relevancy: 0.92,
      exists: true,
      similarity: 0.85,
      citation: "Journal of Materials Chemistry A, 12(8), 4523-4531",
      methodology: "Synthesized Fe-doped LLZO via solid-state reaction. Characterized using XRD, SEM, and EIS.",
      findings: "Fe doping at 3-5 mol% increased ionic conductivity by 60% compared to baseline. Optimal performance at 4 mol%.",
      limitations: "Temperature range limited to 25-200°C. Long-term stability not evaluated.",
      equipment: "Tube furnace (Carbolite STF 15/180), Bruker D8 XRD, Zeiss SEM, Gamry Interface 1010E impedance analyzer",
      funding: "$450,000 (NSF DMREF-2234567, DOE BES DE-SC0023456)",
      position: 0,
    },
    {
      id: 2,
      title: "Defect Chemistry in Lithium Lanthanum Titanate Solid Electrolytes",
      authors: "Kumar, R., Singh, P., Liu, X.",
      year: 2023,
      relevancy: 0.78,
      exists: true,
      similarity: 0.62,
      citation: "Solid State Ionics, 391, 116142",
      methodology: "Computational modeling using DFT to predict defect formation energies.",
      findings: "Oxygen vacancies enhance Li⁺ mobility. Fe²⁺ substitution creates favorable defect structures.",
      limitations: "Purely computational study. Experimental validation needed.",
      equipment: "High-performance computing cluster (512 CPU cores), VASP software package",
      funding: "$280,000 (European Research Council ERC-2022-STG-101039847)",
      position: 1,
    },
    {
      id: 3,
      title: "High-Temperature Stability of Doped Garnet Electrolytes",
      authors: "Yamamoto, T., Chen, W.",
      year: 2025,
      relevancy: 0.68,
      exists: true,
      similarity: 0.45,
      citation: "Advanced Energy Materials, 15(3), 2402156",
      methodology: "Long-term thermal cycling tests up to 300°C on various doped LLZO samples.",
      findings: "Phase stability maintained for Al and Ta dopants. Fe-doped samples showed minor decomposition above 250°C.",
      limitations: "Did not investigate ionic conductivity at elevated temperatures.",
      equipment: "Environmental chamber (Espec SU-262), Rigaku SmartLab XRD, TGA Q500",
      funding: "$620,000 (JSPS KAKENHI JP23H01234, NEDO project 20230045)",
      position: 2,
    },
    {
      id: 4,
      title: "Systematic Study of Transition Metal Dopants in LLZO",
      authors: "Mueller, J., Schmidt, A.",
      year: 2024,
      relevancy: 0.88,
      exists: false,
      similarity: 0.95,
      citation: "N/A - Proposed Study",
      methodology: "Proposed: Comprehensive screening of 3d transition metals (Fe, Co, Ni, Cu, Zn) at varying concentrations.",
      findings: "N/A - Study not yet conducted. Your proposed experiment fills this gap.",
      limitations: "N/A",
      equipment: "N/A - Would require: XRD, SEM, impedance spectroscopy, tube furnace",
      funding: "N/A - Estimated budget: $500,000",
      position: 3,
    },
    {
      id: 5,
      title: "Machine Learning Predictions for Solid Electrolyte Performance",
      authors: "Park, S., Kim, J., Lee, H.",
      year: 2025,
      relevancy: 0.55,
      exists: true,
      similarity: 0.38,
      citation: "Nature Communications, 16, 1234",
      methodology: "Trained ML models on 2000+ solid electrolyte compositions to predict conductivity.",
      findings: "Model predicts Fe-doped LLZO should show 40-70% improvement in conductivity.",
      limitations: "Model predictions require experimental validation.",
      equipment: "GPU cluster (16x NVIDIA A100), PyTorch, Materials Project database",
      funding: "$380,000 (EPSRC EP/W012456/1, Samsung Advanced Institute of Technology)",
      position: 4,
    },
  ];

  return allStudies.sort(() => Math.random() - 0.5).slice(0, 5).map((study, idx) => ({
    ...study,
    position: idx,
  }));
};

export function LiteratureReview({ experiment, onProceedToDashboard }: LiteratureReviewProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [studies, setStudies] = useState<Study[]>([]);
  const [selectedStudy, setSelectedStudy] = useState<Study | null>(null);
  const [showPrompt, setShowPrompt] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setStudies(generateMockStudies(experiment));
      setIsLoading(false);
    }, 3000);

    return () => clearTimeout(timer);
  }, [experiment]);

  const handleStudyClick = (studyId: number) => {
    const study = studies.find(s => s.id === studyId);
    if (study) {
      setSelectedStudy(study);
    }
  };

  const existingStudies = studies.filter(s => s.exists);
  const noveltyScore = studies.length > 0 ? ((studies.filter(s => !s.exists).length / studies.length) * 10).toFixed(1) : "0.0";
  const avgRelevancy = studies.length > 0 ? (studies.reduce((sum, s) => sum + s.relevancy, 0) / studies.length * 100).toFixed(0) : "0";

  return (
    <div className="w-full h-full bg-gradient-to-br from-amber-50 via-yellow-50 to-orange-50 relative flex flex-col">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-green-100/30 via-transparent to-transparent pointer-events-none" />

      <div className="absolute top-20 left-20 w-96 h-96 bg-green-200/15 rounded-full blur-3xl animate-pulse pointer-events-none" />
      <div className="absolute bottom-20 right-20 w-96 h-96 bg-emerald-200/15 rounded-full blur-3xl animate-pulse pointer-events-none" style={{ animationDelay: "1s" }} />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-teal-100/10 rounded-full blur-3xl pointer-events-none" />

      <div className="relative z-10 w-full flex-1 flex flex-col min-h-0">
        {!isLoading && (
          <div className="p-8 border-b border-amber-200">
            <div className="bg-yellow-50/50 rounded-2xl p-6 border border-amber-200 shadow-lg">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-3xl font-light text-stone-900 mb-2">
                    Literature Review
                  </h2>
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
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center"
              >
                <Loader2 className="w-12 h-12 text-green-600 animate-spin mx-auto mb-4" />
                <div className="text-xl text-stone-900 mb-2">Searching Literature</div>
                <div className="text-stone-700">Analyzing databases and publications...</div>
              </motion.div>
            </div>
          ) : (
            <div className="flex-1 overflow-y-auto p-8">
              <div className="max-w-4xl mx-auto space-y-4">
                {studies.map((study, index) => (
                  <motion.div
                    key={study.id}
                    initial={{ opacity: 0, y: 20, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    transition={{ delay: index * 0.1, type: "spring", stiffness: 100 }}
                    onClick={() => handleStudyClick(study.id)}
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
                          <div className="flex items-center gap-2">
                            <Users className="w-4 h-4" />
                            <span>{study.authors}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Calendar className="w-4 h-4" />
                            <span>{study.year}</span>
                          </div>
                        </div>

                        <div className="flex items-center gap-3 flex-wrap">
                          <div className="px-3 py-1.5 bg-teal-50 border border-teal-200 rounded-full text-xs text-teal-700 font-medium">
                            {(study.relevancy * 100).toFixed(0)}% relevant
                          </div>
                          <div className="px-3 py-1.5 bg-emerald-50 border border-emerald-200 rounded-full text-xs text-emerald-700 font-medium">
                            {(study.similarity * 100).toFixed(0)}% similar
                          </div>
                          <div className={`px-3 py-1.5 rounded-full text-xs font-medium ${
                            study.exists
                              ? "bg-green-50 border border-green-200 text-green-700"
                              : "bg-amber-50 border border-amber-200 text-amber-700"
                          }`}>
                            {study.exists ? "Existing Study" : "Research Gap"}
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
              exit={{ x: 400, opacity: 0 }}
              className="w-[500px] bg-orange-50/30 border-l border-amber-200 overflow-y-auto shadow-xl"
            >
              <div className="p-6">
                <div className="flex items-start justify-between mb-6">
                  <div className="flex items-center gap-3">
                    {selectedStudy.exists ? (
                      <div className="w-12 h-12 rounded-xl bg-green-100 border border-green-300 flex items-center justify-center">
                        <CheckCircle2 className="w-6 h-6 text-green-700" />
                      </div>
                    ) : (
                      <div className="w-12 h-12 rounded-xl bg-amber-100 border border-amber-300 flex items-center justify-center">
                        <XCircle className="w-6 h-6 text-amber-700" />
                      </div>
                    )}
                    <div>
                      <div className="text-sm text-stone-800 font-medium">
                        {selectedStudy.exists ? "Existing Study" : "Research Gap"}
                      </div>
                      <div className="text-xs text-stone-600">{selectedStudy.citation}</div>
                    </div>
                  </div>
                  <button onClick={() => setSelectedStudy(null)} className="text-stone-600 hover:text-stone-900 transition-colors">
                    <X className="w-5 h-5" />
                  </button>
                </div>

                <h3 className="text-xl text-stone-900 font-medium mb-4 leading-tight">{selectedStudy.title}</h3>

                <div className="space-y-4 mb-6">
                  <div className="flex items-center gap-4 text-sm">
                    <div className="flex items-center gap-2 text-stone-700">
                      <Users className="w-4 h-4" />
                      {selectedStudy.authors}
                    </div>
                    <div className="flex items-center gap-2 text-stone-700">
                      <Calendar className="w-4 h-4" />
                      {selectedStudy.year}
                    </div>
                  </div>

                  <div className="flex gap-3">
                    <div className="flex-1 p-4 bg-teal-50 border border-teal-200 rounded-xl">
                      <div className="text-xs text-teal-700 mb-1 font-medium">Relevancy</div>
                      <div className="text-2xl text-stone-900 font-light">{(selectedStudy.relevancy * 100).toFixed(0)}%</div>
                    </div>
                    <div className="flex-1 p-4 bg-emerald-50 border border-emerald-200 rounded-xl">
                      <div className="text-xs text-emerald-700 mb-1 font-medium">Similarity</div>
                      <div className="text-2xl text-stone-900 font-light">{(selectedStudy.similarity * 100).toFixed(0)}%</div>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="bg-yellow-50/50 border border-amber-200 rounded-xl p-4">
                    <div className="text-sm text-stone-800 mb-2 font-medium">Equipment Used</div>
                    <div className="text-sm text-stone-700 leading-relaxed">{selectedStudy.equipment}</div>
                  </div>

                  <div className="bg-yellow-50/50 border border-amber-200 rounded-xl p-4">
                    <div className="text-sm text-stone-800 mb-2 font-medium">Funding</div>
                    <div className="text-sm text-stone-700 leading-relaxed">{selectedStudy.funding}</div>
                  </div>

                  <div className="bg-yellow-50/50 border border-amber-200 rounded-xl p-4">
                    <div className="text-sm text-stone-800 mb-2 font-medium">Methodology</div>
                    <div className="text-sm text-stone-700 leading-relaxed">{selectedStudy.methodology}</div>
                  </div>

                  <div className="bg-yellow-50/50 border border-amber-200 rounded-xl p-4">
                    <div className="text-sm text-stone-800 mb-2 font-medium">Findings</div>
                    <div className="text-sm text-stone-700 leading-relaxed">{selectedStudy.findings}</div>
                  </div>

                  {selectedStudy.exists && (
                    <div className="bg-yellow-50/50 border border-amber-200 rounded-xl p-4">
                      <div className="text-sm text-stone-800 mb-2 font-medium">Limitations</div>
                      <div className="text-sm text-stone-700 leading-relaxed">{selectedStudy.limitations}</div>
                    </div>
                  )}
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
