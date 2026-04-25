import { motion } from "motion/react";

interface DNAHelixProps {
  className?: string;
  size?: number;
}

export function DNAHelix({ className = "", size = 300 }: DNAHelixProps) {
  const strands = 12;
  const radius = size * 0.15;

  return (
    <div className={`pointer-events-none ${className}`}>
      <motion.svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        animate={{ rotateY: 360 }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: "linear",
        }}
        style={{
          transformStyle: "preserve-3d",
        }}
      >
        <defs>
          <linearGradient id="helixGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#60A5FA" stopOpacity="0.3" />
            <stop offset="50%" stopColor="#3B82F6" stopOpacity="0.5" />
            <stop offset="100%" stopColor="#60A5FA" stopOpacity="0.3" />
          </linearGradient>
        </defs>

        {Array.from({ length: strands }).map((_, i) => {
          const angle = (i / strands) * Math.PI * 4;
          const y = (i / strands) * size;

          const x1 = size / 2 + Math.cos(angle) * radius;
          const x2 = size / 2 + Math.cos(angle + Math.PI) * radius;

          const nextAngle = ((i + 1) / strands) * Math.PI * 4;
          const nextY = ((i + 1) / strands) * size;
          const nextX1 = size / 2 + Math.cos(nextAngle) * radius;
          const nextX2 = size / 2 + Math.cos(nextAngle + Math.PI) * radius;

          return (
            <g key={i}>
              <motion.path
                d={`M ${x1} ${y} Q ${size / 2} ${(y + nextY) / 2} ${nextX1} ${nextY}`}
                stroke="url(#helixGradient)"
                strokeWidth="2"
                fill="none"
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{ pathLength: 1, opacity: 1 }}
                transition={{
                  duration: 2,
                  delay: i * 0.1,
                  ease: "easeInOut",
                }}
              />

              <motion.path
                d={`M ${x2} ${y} Q ${size / 2} ${(y + nextY) / 2} ${nextX2} ${nextY}`}
                stroke="url(#helixGradient)"
                strokeWidth="2"
                fill="none"
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{ pathLength: 1, opacity: 1 }}
                transition={{
                  duration: 2,
                  delay: i * 0.1,
                  ease: "easeInOut",
                }}
              />

              <motion.line
                x1={x1}
                y1={y}
                x2={x2}
                y2={y}
                stroke="#3B82F6"
                strokeWidth="1"
                strokeOpacity="0.2"
                initial={{ opacity: 0 }}
                animate={{ opacity: 0.2 }}
                transition={{
                  duration: 1,
                  delay: i * 0.1,
                }}
              />

              <motion.circle
                cx={x1}
                cy={y}
                r="4"
                fill="#60A5FA"
                opacity="0.6"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{
                  duration: 0.5,
                  delay: i * 0.1,
                }}
              />

              <motion.circle
                cx={x2}
                cy={y}
                r="4"
                fill="#3B82F6"
                opacity="0.6"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{
                  duration: 0.5,
                  delay: i * 0.1,
                }}
              />
            </g>
          );
        })}
      </motion.svg>
    </div>
  );
}
