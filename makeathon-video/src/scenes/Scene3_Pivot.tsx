import React from "react";
import { AbsoluteFill, useCurrentFrame, spring } from "remotion";
import { colors } from "../constants/colors";
import type { Layout } from "../constants/layout";
import { countUp, opacityIn } from "../components/animations";

export const Scene3_Pivot: React.FC<{ layout: Layout }> = ({ layout }) => {
  const frame = useCurrentFrame();
  const soScale = spring({ frame: frame - 5, fps: 30, config: { damping: 10, stiffness: 150 } });

  return (
    <AbsoluteFill style={{ backgroundColor: colors.bg, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", fontFamily: '"Inter", sans-serif' }}>
      <div style={{ fontSize: layout.titleSize * 1.5, fontWeight: 500, color: colors.amber, transform: `scale(${Math.max(0, soScale)})`, opacity: opacityIn(frame, 0), lineHeight: 1 }}>So.</div>
      <div style={{ marginTop: 32, opacity: opacityIn(frame, 35), textAlign: "center" }}>
        <div style={{ fontSize: layout.bodySize, fontWeight: 500, color: colors.textPrimary, lineHeight: 1.4 }}>
          I scraped every entry.
        </div>
        <div style={{ fontSize: layout.smallSize, fontWeight: 500, color: colors.textMuted, lineHeight: 1.4, marginTop: 8 }}>
          From every edition.
        </div>
      </div>
      <div style={{ marginTop: 40, opacity: opacityIn(frame, 55), display: "flex", alignItems: "baseline", gap: 12 }}>
        <span style={{ fontSize: layout.statSize, fontWeight: 500, color: colors.amber, lineHeight: 1 }}>{countUp(frame, 55, 15, 318)}</span>
        <span style={{ fontSize: layout.smallSize, fontWeight: 500, color: colors.textMuted }}>submissions</span>
      </div>
    </AbsoluteFill>
  );
};
