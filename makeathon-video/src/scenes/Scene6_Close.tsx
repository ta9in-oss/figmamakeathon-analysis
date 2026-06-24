import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate } from "remotion";
import { colors } from "../constants/colors";
import type { Layout } from "../constants/layout";
import { opacityIn } from "../components/animations";

export const Scene6_Close: React.FC<{ layout: Layout }> = ({ layout }) => {
  const frame = useCurrentFrame();
  const fadeOut = 1 - interpolate(frame, [100, 120], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: colors.bg, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", opacity: fadeOut }}>
      <div style={{ fontSize: 28, fontWeight: 500, color: colors.textMuted, opacity: opacityIn(frame, 0), marginBottom: 16 }}>Full analysis and data</div>
      <div style={{ fontSize: 52, fontWeight: 500, color: colors.amber, opacity: opacityIn(frame, 8), position: "relative" }}>
        figmamakeathon.ta9in.com
        <div style={{ position: "absolute", bottom: -4, left: 0, height: 2, backgroundColor: colors.amber, width: `${Math.min(1, Math.max(0, (frame-25)/30)*1)*100}%`, transition: "none" }}>
          <div style={{ height: 2, width: "100%", backgroundColor: colors.amber, transform: `scaleX(${Math.min(1, Math.max(0, (frame-25)/30))})`, transformOrigin: "left" }} />
        </div>
      </div>
    </AbsoluteFill>
  );
};
