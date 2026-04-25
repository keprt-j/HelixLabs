import { motion } from "motion/react";
import { useState, useEffect } from "react";

interface Study {
  id: number;
  title: string;
  exists: boolean;
  relevancy: number;
  position: number;
}

interface InteractiveHelixProps {
  studies: Study[];
  onStudyClick: (studyId: number) => void;
  isLoading: boolean;
}

export function InteractiveHelix({ studies, onStudyClick, isLoading }: InteractiveHelixProps) {
  const [hoveredId, setHoveredId] = useState<number | null>(null);
  const [flash, setFlash] = useState(false);
  const segments = 40;
  const helixRadius = 100;
  const helixHeight = 500;

  useEffect(() => {
    if (!isLoading && studies.length > 0) {
      setFlash(true);
      const timer = setTimeout(() => setFlash(false), 1000);
      return () => clearTimeout(timer);
    }
  }, [isLoading, studies.length]);

  const [studyPositions] = useState(() => [
    { segment: 0, strand: Math.random() > 0.5 ? 1 : 2 },
    { segment: 8, strand: Math.random() > 0.5 ? 1 : 2 },
    { segment: 16, strand: Math.random() > 0.5 ? 1 : 2 },
    { segment: 24, strand: Math.random() > 0.5 ? 1 : 2 },
    { segment: 32, strand: Math.random() > 0.5 ? 1 : 2 },
  ]);

  return (
    <div className="relative w-full h-full flex items-center justify-center" style={{ perspective: "1200px" }}>
      <motion.div
        className="relative"
        style={{
          width: 300,
          height: helixHeight,
          transformStyle: "preserve-3d",
        }}
        animate={{
          rotateY: isLoading ? 360 : 0,
        }}
        transition={
          isLoading
            ? {
                duration: 15,
                repeat: Infinity,
                ease: "linear",
              }
            : {
                duration: 2.5,
                ease: "easeOut",
              }
        }
      >
        {Array.from({ length: segments }).map((_, i) => {
          const progress = i / segments;
          const angle = progress * Math.PI * 6;
          const y = progress * helixHeight;

          const x1 = Math.cos(angle) * helixRadius;
          const z1 = Math.sin(angle) * helixRadius;

          const x2 = Math.cos(angle + Math.PI) * helixRadius;
          const z2 = Math.sin(angle + Math.PI) * helixRadius;

          const studyMatch = studyPositions.find(sp => sp.segment === i);
          const studyIndex = studyMatch ? studyPositions.indexOf(studyMatch) : -1;
          const hasStudy = !isLoading && studyMatch && studyIndex < studies.length;
          const study = hasStudy ? studies[studyIndex] : null;
          const isStrand1 = studyMatch?.strand === 1;
          const isStrand2 = studyMatch?.strand === 2;
          const isHovered = study && hoveredId === study.id;

          const getNodeProps = (isStudyNode: boolean, x: number, z: number) => {
            if (isStudyNode && study) {
              return {
                width: 14,
                height: 14,
                background: study.exists
                  ? "linear-gradient(135deg, #10B981, #059669)"
                  : "linear-gradient(135deg, #F59E0B, #D97706)",
                boxShadow: study.exists
                  ? `0 0 ${isHovered ? "40px" : "25px"} rgba(16, 185, 129, ${isHovered ? "1" : "0.8"})`
                  : `0 0 ${isHovered ? "40px" : "25px"} rgba(245, 158, 11, ${isHovered ? "1" : "0.8"})`,
                cursor: "pointer",
                border: isHovered ? "2px solid white" : "none",
              };
            }
            return {
              width: 12,
              height: 12,
              background: "linear-gradient(135deg, #22D3EE, #3B82F6)",
              boxShadow: "0 0 15px rgba(34, 211, 238, 0.6)",
              cursor: "default",
              border: "none",
            };
          };

          const node1Props = getNodeProps(hasStudy && isStrand1, x1, z1);
          const node2Props = getNodeProps(hasStudy && isStrand2, x2, z2);

          return (
            <div key={i} style={{ transformStyle: "preserve-3d" }}>
              <motion.div
                className="absolute rounded-full"
                style={{
                  width: node1Props.width,
                  height: node1Props.height,
                  top: y,
                  left: "50%",
                  transform: `translate(-50%, -50%) translate3d(${x1}px, 0, ${z1}px)`,
                  background: node1Props.background,
                  cursor: node1Props.cursor,
                  border: node1Props.border,
                }}
                animate={{
                  boxShadow: flash
                    ? hasStudy && isStrand1 && study
                      ? study.exists
                        ? [
                            "0 0 25px rgba(16, 185, 129, 0.8)",
                            "0 0 80px rgba(16, 185, 129, 1)",
                            "0 0 25px rgba(16, 185, 129, 0.8)",
                          ]
                        : [
                            "0 0 25px rgba(245, 158, 11, 0.8)",
                            "0 0 80px rgba(245, 158, 11, 1)",
                            "0 0 25px rgba(245, 158, 11, 0.8)",
                          ]
                      : [
                          "0 0 15px rgba(34, 211, 238, 0.6)",
                          "0 0 60px rgba(34, 211, 238, 1)",
                          "0 0 15px rgba(34, 211, 238, 0.6)",
                        ]
                    : node1Props.boxShadow,
                }}
                transition={{ duration: 1, delay: hasStudy && isStrand1 ? studyIndex * 0.15 : 0 }}
                onMouseEnter={() => hasStudy && isStrand1 && study && setHoveredId(study.id)}
                onMouseLeave={() => hasStudy && isStrand1 && setHoveredId(null)}
                onClick={() => hasStudy && isStrand1 && study && onStudyClick(study.id)}
                whileHover={hasStudy && isStrand1 ? { scale: 1.4 } : {}}
              >
                {hasStudy && isStrand1 && study && isHovered && (
                  <motion.div
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="absolute left-8 top-1/2 -translate-y-1/2 bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 shadow-xl pointer-events-none"
                    style={{ width: "300px", whiteSpace: "normal", zIndex: 50 }}
                  >
                    <div className="text-xs text-white line-clamp-2">{study.title}</div>
                    <div className="text-xs text-gray-500 mt-1">
                      {study.exists ? "Existing Study" : "Research Gap"} • {(study.relevancy * 100).toFixed(0)}% relevant
                    </div>
                  </motion.div>
                )}
              </motion.div>

              <motion.div
                className="absolute rounded-full"
                style={{
                  width: node2Props.width,
                  height: node2Props.height,
                  top: y,
                  left: "50%",
                  transform: `translate(-50%, -50%) translate3d(${x2}px, 0, ${z2}px)`,
                  background: node2Props.background,
                  cursor: node2Props.cursor,
                  border: node2Props.border,
                }}
                animate={{
                  boxShadow: flash
                    ? hasStudy && isStrand2 && study
                      ? study.exists
                        ? [
                            "0 0 25px rgba(16, 185, 129, 0.8)",
                            "0 0 80px rgba(16, 185, 129, 1)",
                            "0 0 25px rgba(16, 185, 129, 0.8)",
                          ]
                        : [
                            "0 0 25px rgba(245, 158, 11, 0.8)",
                            "0 0 80px rgba(245, 158, 11, 1)",
                            "0 0 25px rgba(245, 158, 11, 0.8)",
                          ]
                      : [
                          "0 0 15px rgba(99, 102, 241, 0.6)",
                          "0 0 60px rgba(99, 102, 241, 1)",
                          "0 0 15px rgba(99, 102, 241, 0.6)",
                        ]
                    : node2Props.boxShadow,
                }}
                transition={{ duration: 1, delay: hasStudy && isStrand2 ? studyIndex * 0.15 : 0 }}
                onMouseEnter={() => hasStudy && isStrand2 && study && setHoveredId(study.id)}
                onMouseLeave={() => hasStudy && isStrand2 && setHoveredId(null)}
                onClick={() => hasStudy && isStrand2 && study && onStudyClick(study.id)}
                whileHover={hasStudy && isStrand2 ? { scale: 1.4 } : {}}
              >
                {hasStudy && isStrand2 && study && isHovered && (
                  <motion.div
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="absolute left-8 top-1/2 -translate-y-1/2 bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 shadow-xl pointer-events-none"
                    style={{ width: "300px", whiteSpace: "normal", zIndex: 50 }}
                  >
                    <div className="text-xs text-white line-clamp-2">{study.title}</div>
                    <div className="text-xs text-gray-500 mt-1">
                      {study.exists ? "Existing Study" : "Research Gap"} • {(study.relevancy * 100).toFixed(0)}% relevant
                    </div>
                  </motion.div>
                )}
              </motion.div>

            </div>
          );
        })}
      </motion.div>

      {!isLoading && studies.length > 0 && (
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 text-center">
          <div className="text-sm text-gray-500 mb-2">Click on a node to view study details</div>
          <div className="flex items-center justify-center gap-6">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-gradient-to-br from-green-500 to-green-600" />
              <span className="text-xs text-gray-400">Existing Studies</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-gradient-to-br from-yellow-500 to-yellow-600" />
              <span className="text-xs text-gray-400">Research Gaps</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
