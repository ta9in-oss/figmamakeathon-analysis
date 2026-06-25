import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate, Easing } from "remotion";
import { colors } from "../constants/colors";
import type { Layout } from "../constants/layout";
import { opacityIn, pushIn } from "../components/animations";

export const Scene6_Close: React.FC<{ layout: Layout }> = ({ layout }) => {
  const frame = useCurrentFrame();

  const fadeOut = 1 - interpolate(frame, [100, 120], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const underlineScale = interpolate(frame, [25, 55], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const scale = pushIn(frame, 120, 1, 1.05);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: colors.bg,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        opacity: fadeOut,
        padding: `0 ${layout.padding}px`,
        fontFamily: '"Inter", sans-serif',
        transform: `scale(${scale})`,
        transformOrigin: "center",
      }}
    >
      <div
        style={{
          fontSize: layout.smallSize,
          fontWeight: 500,
          color: colors.textMuted,
          opacity: opacityIn(frame, 0),
          marginBottom: 16,
        }}
      >
        Full analysis and data
      </div>
      <div
        style={{
          fontSize: layout.bodySize * 1.1,
          fontWeight: 600,
          color: colors.amber,
          textShadow: "0 0 48px rgba(239,159,39,0.4)",
          opacity: opacityIn(frame, 8),
          position: "relative",
          display: "inline-block",
        }}
      >
        figmamakeathon.ta9in.com
        <div
          style={{
            position: "absolute",
            bottom: -4,
            left: 0,
            right: 0,
            height: 2,
            backgroundColor: colors.amber,
            transform: `scaleX(${underlineScale})`,
            transformOrigin: "left",
          }}
        />
      </div>
    </AbsoluteFill>
  );
};
