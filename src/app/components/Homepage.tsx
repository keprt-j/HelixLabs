import { useState } from "react";
import { motion } from "motion/react";
import { ArrowRight, Beaker, Cpu, Loader2, Network, Search } from "lucide-react";
import { HelixAnimation } from "./HelixAnimation";

interface HomepageProps {
  onStartReview: (experiment: string) => void | Promise<void>;
}

export function Homepage({ onStartReview }: HomepageProps) {
  const [experiment, setExperiment] = useState("");
  const [busy, setBusy] = useState(false);

  const handleSubmit = async () => {
    if (!experiment.trim() || busy) return;
    setBusy(true);
    try {
      await onStartReview(experiment);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="w-full h-full bg-gradient-to-br from-amber-50 via-yellow-50 to-orange-50 overflow-hidden relative">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-green-100/30 via-transparent to-transparent" />

      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-green-200/15 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-emerald-200/15 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 w-full h-full flex">
        <div className="flex-1 flex flex-col justify-center px-16 max-w-2xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <div className="mb-6 inline-flex items-center gap-2 px-4 py-2 rounded-full bg-green-600/10 border border-green-600/30">
              <div className="w-2 h-2 bg-green-600 rounded-full animate-pulse" />
              <span className="text-sm text-green-800 tracking-wide font-medium">AUTONOMOUS LABORATORY OS</span>
            </div>

            <h1 className="text-7xl font-light text-stone-900 mb-6 tracking-tight">
              Helix<span className="font-normal">Labs</span>
            </h1>

            <p className="text-xl text-stone-700 mb-8 leading-relaxed font-light">
              The operating system for autonomous cloud laboratories.
              <br />
              Compile, schedule, execute, and iterate scientific experiments.
            </p>

            <div className="mb-8">
              <div className="text-sm text-stone-700 mb-3 font-medium">What experiment do you want to run?</div>
              <div className="flex gap-3">
                <input
                  type="text"
                  value={experiment}
                  onChange={(e) => setExperiment(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && !busy && void handleSubmit()}
                  placeholder="e.g., Investigate Fe-doped LLZO ionic conductivity at varying temperatures"
                  className="flex-1 px-4 py-4 bg-yellow-50/50 border border-amber-200 rounded-lg text-stone-900 placeholder-stone-400 focus:outline-none focus:border-green-600 focus:ring-2 focus:ring-green-500/20 transition-all"
                />
                <motion.button
                  onClick={() => void handleSubmit()}
                  disabled={!experiment.trim() || busy}
                  className="px-8 py-4 bg-green-700 hover:bg-green-800 disabled:bg-amber-200 disabled:cursor-not-allowed text-white rounded-lg flex items-center gap-3 transition-all shadow-lg"
                  whileHover={{ scale: experiment.trim() && !busy ? 1.02 : 1 }}
                  whileTap={{ scale: experiment.trim() && !busy ? 0.98 : 1 }}
                >
                  {busy ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
                  <span className="font-medium">{busy ? "Starting…" : "Review Literature"}</span>
                </motion.button>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.2 }}
                className="flex items-start gap-3"
              >
                <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center flex-shrink-0">
                  <Beaker className="w-5 h-5 text-green-700" />
                </div>
                <div>
                  <div className="text-sm font-medium text-stone-900 mb-1">Experiment Compiler</div>
                  <div className="text-xs text-stone-600">Structured planning</div>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.3 }}
                className="flex items-start gap-3"
              >
                <div className="w-10 h-10 rounded-lg bg-emerald-100 flex items-center justify-center flex-shrink-0">
                  <Network className="w-5 h-5 text-emerald-700" />
                </div>
                <div>
                  <div className="text-sm font-medium text-stone-900 mb-1">Claim Graphs</div>
                  <div className="text-xs text-stone-600">Hypothesis tracking</div>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.4 }}
                className="flex items-start gap-3"
              >
                <div className="w-10 h-10 rounded-lg bg-teal-100 flex items-center justify-center flex-shrink-0">
                  <Cpu className="w-5 h-5 text-teal-700" />
                </div>
                <div>
                  <div className="text-sm font-medium text-stone-900 mb-1">Auto Recovery</div>
                  <div className="text-xs text-stone-600">Smart error handling</div>
                </div>
              </motion.div>
            </div>
          </motion.div>
        </div>

        <div className="flex-1 flex items-center justify-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1, delay: 0.2 }}
          >
            <HelixAnimation />
          </motion.div>
        </div>
      </div>

      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 text-center">
        <div className="text-xs text-stone-600 font-medium tracking-wider">
          EXPERIMENT LIFECYCLE: COMPILE → VALIDATE → SCHEDULE → EXECUTE → RECOVER → INTERPRET → ITERATE
        </div>
      </div>
    </div>
  );
}
