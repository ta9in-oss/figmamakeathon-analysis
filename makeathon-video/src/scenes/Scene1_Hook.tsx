import React from "react";
import { AbsoluteFill, useCurrentFrame, spring } from "remotion";
import { colors } from "../constants/colors";
import type { Layout } from "../constants/layout";

export const Scene1_Hook: React.FC<{ layout: Layout }> = ({ layout }) => {
  const frame = useCurrentFrame();

  const words = [
    { text: "How", delay: 0 },
    { text: "to", delay: 6 },
    { text: "actually", delay: 12, color: colors.teal },
    { text: "win", delay: 20 },
    { text: "a", delay: 28 },
    { text: "Figma", delay: 36, color: colors.amber },
    { text: "Makeathon?", delay: 44, color: colors.amber },
  ];

  const qMarkScale = spring({ frame: frame - 80, fps: 30, config: { damping: 8, stiffness: 200 } });
  const qMarkPulse = 1 + (qMarkScale > 0 ? qMarkScale * 0.1 : 0);

  return (
    <AbsoluteFill style={{ backgroundColor: colors.bg, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: "0.4em 0.6em", maxWidth: layout.maxWidth, padding: layout.padding, fontSize: layout.titleSize, fontWeight: 500, lineHeight: 1.15, color: colors.textPrimary }}>
        {words.map((w, i) => {
          const active = frame - w.delay;
          const y = active < 0 ? 24 : active < 12 ? 24 - (active / 12) * 24 : 0;
          const opacity = active < 0 ? 0 : active < 8 ? active / 8 : 1;
          const isQM = w.text === "Makeathon?";
          return (
            <span key={i} style={{ opacity, transform: `translateY(${y}px)`, color: w.color || colors.textPrimary, transformOrigin: "center center", ...(isQM ? { transform: `translateY(${y}px) scale(${qMarkPulse})` } : {}) }}>
              {w.text}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
