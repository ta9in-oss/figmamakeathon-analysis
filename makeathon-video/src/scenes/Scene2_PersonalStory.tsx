import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate, spring, Sequence } from "remotion";
import { colors } from "../constants/colors";
import type { Layout } from "../constants/layout";
import { countUp, opacityIn } from "../components/animations";

const Act: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AbsoluteFill style={{ backgroundColor: colors.bg, display: "flex", flexDirection: "column", justifyContent: "center", padding: "0 120px" }}>{children}</AbsoluteFill>
);

const Line: React.FC<{ text: string; delay?: number; color?: string; size?: number; italic?: boolean }> = ({ text, delay = 0, color = colors.textPrimary, size, italic }) => {
  const frame = useCurrentFrame();
  const active = frame - delay;
  const y = active < 0 ? 24 : active < 12 ? 24 - (active / 12) * 24 : 0;
  const opacity = active < 0 ? 0 : active < 8 ? active / 8 : 1;
  return (
    <div style={{ opacity, transform: `translateY(${y}px)`, fontSize: size || 48, fontWeight: 500, color, lineHeight: 1.3, fontStyle: italic ? "italic" : "normal", marginBottom: 8 }}>
      {text}
    </div>
  );
};

export const Scene2_PersonalStory: React.FC<{ layout: Layout }> = ({ layout }) => {
  const frame = useCurrentFrame();

  return (
    <>
      {/* Act 2a — The project */}
      <Sequence from={0} durationInFrames={120}>
        <Act>
          <Line text="I built Bubble War." delay={0} />
          <Line text="A real-time multiplayer typing game." delay={12} color={colors.textMuted} size={36} />
          <Line text="I thought it would win." delay={28} size={36} />
        </Act>
      </Sequence>

      {/* Act 2b — The submission */}
      <Sequence from={120} durationInFrames={120}>
        <Act>
          <Line text="I published my entry" delay={0} />
          <Line text="13 hours before the deadline." delay={12} color={colors.amber} />
          <div style={{ marginTop: 40, width: "100%", maxWidth: 1000, height: 8, backgroundColor: colors.borderDim, borderRadius: 4, position: "relative", overflow: "hidden" }}>
            <div style={{ height: "100%", backgroundColor: colors.gray, borderRadius: 4 }} />
            <div style={{ position: "absolute", top: -6, right: `${(13/336)*100}%`, width: 4, height: 20, backgroundColor: colors.amber, borderRadius: 2, opacity: opacityIn(frame, 60) }} />
            <div style={{ position: "absolute", top: 14, right: `${(13/336)*100}%`, fontSize: 18, color: colors.amber, opacity: opacityIn(frame, 70), transform: `translateX(50%)` }}>my entry</div>
          </div>
        </Act>
      </Sequence>

      {/* Act 2c — The effort */}
      <Sequence from={240} durationInFrames={120}>
        <Act>
          <Line text="I posted on X. Instagram. TikTok." delay={0} />
          <Line text="I made demo videos." delay={16} color={colors.textMuted} size={36} />
          <Line text="I did everything right." delay={32} />
        </Act>
      </Sequence>

      {/* Act 2d — The result */}
      <Sequence from={360} durationInFrames={150}>
        <Act>
          <div style={{ opacity: opacityIn(frame, 30), fontSize: 72, fontWeight: 500, color: colors.gray, lineHeight: 1.2 }}>But I didn't win.</div>
        </Act>
      </Sequence>

      {/* Act 2e — The insight */}
      <Sequence from={510} durationInFrames={150}>
        <Act>
          <div style={{ display: "flex", alignItems: "baseline", gap: 16 }}>
            <span style={{ fontSize: 120, fontWeight: 500, color: colors.amber, lineHeight: 1 }}>{countUp(frame, 0, 20, 1)}</span>
          </div>
          <Line text="visitor from the US checked my project." delay={24} color={colors.textMuted} size={32} />
          <Line text="The recap video included all the winners." delay={48} color={colors.textPrimary} size={36} />
          <Line text="Before the announcement." delay={60} color={colors.textMuted} size={28} />
          <Line text="Was my project even considered?" delay={76} color={colors.textMuted} size={32} italic={true} />
        </Act>
      </Sequence>
    </>
  );
};
