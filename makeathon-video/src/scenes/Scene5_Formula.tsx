import React from "react";
import { AbsoluteFill, useCurrentFrame, Sequence } from "remotion";
import { colors } from "../constants/colors";
import type { Layout } from "../constants/layout";
import { opacityIn } from "../components/animations";

export const Scene5_Formula: React.FC<{ layout: Layout }> = ({ layout }) => {
  const frame = useCurrentFrame();

  const lines = [
    { text: "Post in the first 3 days.", delay: 0 },
    { text: "Cross-post everywhere.", delay: 8 },
    { text: "Make noise before others do.", delay: 16 },
  ];

  return (
    <AbsoluteFill style={{ backgroundColor: colors.bg, display: "flex", flexDirection: "column", justifyContent: "center", padding: `0 ${layout.padding}px` }}>
      <div style={{ height: 2, width: `${Math.min(1, opacityIn(frame, 0))*100}%`, backgroundColor: colors.amber, marginBottom: 48, transition: "none" }}>
        <div style={{ height: 2, width: "100%", backgroundColor: colors.amber, transform: `scaleX(${Math.min(1, frame/25)})`, transformOrigin: "left" }} />
      </div>
      {lines.map((l, i) => {
        const active = frame - l.delay;
        const y = active < 0 ? 24 : active < 12 ? 24 - (active/12)*24 : 0;
        const opacity = active < 0 ? 0 : active < 8 ? active/8 : 1;
        return (
          <div key={i} style={{ opacity, transform: `translateY(${y}px)`, fontSize: 52, fontWeight: 500, color: i === 0 ? colors.amber : colors.textPrimary, lineHeight: 1.4 }}>
            {l.text}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
