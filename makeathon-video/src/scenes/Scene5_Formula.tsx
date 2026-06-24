import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate, Easing } from "remotion";
import { colors } from "../constants/colors";
import type { Layout } from "../constants/layout";
import { opacityIn } from "../components/animations";

export const Scene5_Formula: React.FC<{ layout: Layout }> = ({ layout }) => {
  const frame = useCurrentFrame();

  const lines = [
    { text: "Post in the first 3 days.", delay: 0, color: colors.amber },
    { text: "Cross-post everywhere.", delay: 8, color: colors.textPrimary },
    { text: "Make noise before others do.", delay: 16, color: colors.textPrimary },
  ];

  const lineScale = interpolate(frame, [0, 25], [0, 1], {
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: colors.bg,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        padding: `0 ${layout.padding}px`,
        fontFamily: '"Inter", sans-serif',
      }}
    >
      <div
        style={{
          height: 2,
          backgroundColor: colors.amber,
          marginBottom: 48,
          transform: `scaleX(${lineScale})`,
          transformOrigin: "left",
        }}
      />
      {lines.map((l, i) => {
        const active = frame - l.delay;
        const y = active < 0 ? 24 : active < 12 ? 24 - (active / 12) * 24 : 0;
        const opacity = active < 0 ? 0 : active < 8 ? active / 8 : 1;
        return (
          <div
            key={i}
            style={{
              opacity,
              transform: `translateY(${y}px)`,
              fontSize: layout.bodySize * 1.1,
              fontWeight: i === 0 ? 600 : 500,
              color: l.color,
              lineHeight: 1.4,
            }}
          >
            {l.text}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
