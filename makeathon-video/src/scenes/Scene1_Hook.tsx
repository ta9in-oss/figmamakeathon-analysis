import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { colors } from "../constants/colors";
import type { Layout } from "../constants/layout";
import { BubbleField } from "../components/BubbleField";
import { dramaIn, pushIn } from "../components/animations";

export const Scene1_Hook: React.FC<{ layout: Layout }> = ({ layout }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();

  const scale = pushIn(frame, 90, 1.04, 1.12);

  const eyebrow = dramaIn(frame, 4, 20);
  const line1 = dramaIn(frame, 18, 46);
  const line2 = dramaIn(frame, 40, 46);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: colors.bg,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontFamily: '"Inter", sans-serif',
      }}
    >
      <AbsoluteFill style={{ transform: `scale(${scale})`, transformOrigin: "center" }}>
        <BubbleField width={width} height={height} />
      </AbsoluteFill>

      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          textAlign: "center",
          maxWidth: layout.maxWidth,
          padding: layout.padding,
          transform: `scale(${scale})`,
          transformOrigin: "center",
        }}
      >
        <div
          style={{
            fontSize: layout.smallSize * 0.82,
            fontWeight: 600,
            letterSpacing: "0.32em",
            textTransform: "uppercase",
            color: colors.textMuted,
            opacity: eyebrow.opacity,
            transform: `translateY(${eyebrow.y}px)`,
            marginBottom: layout.bodySize * 0.9,
          }}
        >
          318 entries · 3 editions · $300K
        </div>

        <div
          style={{
            fontSize: layout.titleSize * 1.04,
            fontWeight: 600,
            lineHeight: 1.08,
            color: colors.textPrimary,
            opacity: line1.opacity,
            transform: `translateY(${line1.y}px)`,
          }}
        >
          Why did they win
        </div>
        <div
          style={{
            fontSize: layout.titleSize * 1.04,
            fontWeight: 600,
            lineHeight: 1.08,
            color: colors.amber,
            textShadow: "0 0 48px rgba(239,159,39,0.4)",
            opacity: line2.opacity,
            transform: `translateY(${line2.y}px)`,
          }}
        >
          and I didn&rsquo;t?
        </div>
      </div>
    </AbsoluteFill>
  );
};
