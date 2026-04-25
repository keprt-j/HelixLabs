import { motion } from "motion/react";

export function HelixAnimation() {
  const segments = 40;
  const helixRadius = 100;
  const helixHeight = 500;

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
          rotateY: 360,
        }}
        transition={{
          duration: 15,
          repeat: Infinity,
          ease: "linear",
        }}
      >
        {Array.from({ length: segments }).map((_, i) => {
          const progress = i / segments;
          const angle = progress * Math.PI * 6;
          const y = progress * helixHeight;

          const x1 = Math.cos(angle) * helixRadius;
          const z1 = Math.sin(angle) * helixRadius;

          const x2 = Math.cos(angle + Math.PI) * helixRadius;
          const z2 = Math.sin(angle + Math.PI) * helixRadius;

          return (
            <div key={i} style={{ transformStyle: "preserve-3d" }}>
              <div
                className="absolute rounded-full"
                style={{
                  width: 12,
                  height: 12,
                  top: y,
                  left: "50%",
                  transform: `translate(-50%, -50%) translate3d(${x1}px, 0, ${z1}px)`,
                  background: "linear-gradient(135deg, #10B981, #059669)",
                  boxShadow: "0 0 15px rgba(16, 185, 129, 0.6)",
                }}
              />

              <div
                className="absolute rounded-full"
                style={{
                  width: 12,
                  height: 12,
                  top: y,
                  left: "50%",
                  transform: `translate(-50%, -50%) translate3d(${x2}px, 0, ${z2}px)`,
                  background: "linear-gradient(135deg, #059669, #047857)",
                  boxShadow: "0 0 15px rgba(5, 150, 105, 0.6)",
                }}
              />
            </div>
          );
        })}
      </motion.div>
    </div>
  );
}
