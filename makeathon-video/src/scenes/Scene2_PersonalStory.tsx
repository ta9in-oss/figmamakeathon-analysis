import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  Sequence,
} from "remotion";
import { colors } from "../constants/colors";
import type { Layout } from "../constants/layout";
import { countUp, opacityIn, pushIn } from "../components/animations";
import { OffthreadVideoClip } from "../components/OffthreadVideoClip";

const Act: React.FC<{
  children: React.ReactNode;
  layout: Layout;
  video?: React.ReactNode;
}> = ({ children, layout, video }) => {
  const frame = useCurrentFrame();
  const scale = pushIn(frame, 130, 1, 1.05);
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
      {video}
      <div
        style={{
          position: "relative",
          zIndex: 1,
          transform: `scale(${scale})`,
          transformOrigin: "left center",
        }}
      >
        {children}
      </div>
    </AbsoluteFill>
  );
};

const Line: React.FC<{
  text: string;
  delay?: number;
  color?: string;
  size?: number;
  italic?: boolean;
  layout: Layout;
}> = ({ text, delay = 0, color, size, italic, layout }) => {
  const frame = useCurrentFrame();
  const active = frame - delay;
  const y = active < 0 ? 24 : active < 12 ? 24 - (active / 12) * 24 : 0;
  const opacity = active < 0 ? 0 : active < 8 ? active / 8 : 1;
  return (
    <div
      style={{
        opacity,
        transform: `translateY(${y}px)`,
        fontSize: size ?? layout.bodySize,
        fontWeight: 500,
        color: color ?? colors.textPrimary,
        lineHeight: 1.35,
        fontStyle: italic ? "italic" : "normal",
        marginBottom: 8,
      }}
    >
      {text}
    </div>
  );
};

export const Scene2_PersonalStory: React.FC<{ layout: Layout }> = ({
  layout,
}) => {
  const frame = useCurrentFrame();

  return (
    <>
      {/* Act 2a — The project (frames 0–119) */}
      <Sequence from={0} durationInFrames={120}>
        <Act layout={layout}>
          <div
            style={{
              fontSize: layout.titleSize * 0.85,
              fontWeight: 600,
              color: colors.textPrimary,
              opacity: opacityIn(frame, 0),
              marginBottom: 12,
            }}
          >
            I built Bubble War.
          </div>
          <Line
            text="A real-time multiplayer game — made entirely in Figma."
            delay={12}
            color={colors.textMuted}
            layout={layout}
          />
          <Line
            text="I thought it would win."
            delay={28}
            color={colors.textPrimary}
            layout={layout}
          />
        </Act>
      </Sequence>

      {/* Act 2b — The submission (frames 120–239) */}
      <Sequence from={120} durationInFrames={120}>
        <Act layout={layout}>
          <Line text="I published my entry" delay={0} layout={layout} />
          <Line
            text="13 hours before the deadline."
            delay={12}
            color={colors.amber}
            layout={layout}
          />
          <div
            style={{
              marginTop: 40,
              width: "100%",
              maxWidth: layout.maxWidth,
              height: 6,
              backgroundColor: colors.border,
              borderRadius: 4,
              position: "relative",
              overflow: "visible",
            }}
          >
            <div
              style={{
                height: "100%",
                backgroundColor: colors.gray,
                borderRadius: 4,
                width: "100%",
              }}
            />
            <div
              style={{
                position: "absolute",
                top: -8,
                right: `${(13 / 336) * 100}%`,
                width: 3,
                height: 22,
                backgroundColor: colors.amber,
                borderRadius: 2,
                opacity: opacityIn(frame, 60),
              }}
            />
            <div
              style={{
                position: "absolute",
                top: 18,
                right: `${(13 / 336) * 100}%`,
                fontSize: layout.smallSize,
                color: colors.amber,
                opacity: opacityIn(frame, 70),
                transform: "translateX(50%)",
                whiteSpace: "nowrap",
              }}
            >
              my entry
            </div>
          </div>
        </Act>
      </Sequence>

      {/* Act 2c — The effort with gameplay video bg (frames 240–359) */}
      <Sequence from={240} durationInFrames={120}>
        <Act
          layout={layout}
          video={
            <OffthreadVideoClip
              src="bubble-war-1.mp4"
              startFrom={0}
              opacity={0.9}
            />
          }
        >
          <Line
            text="I posted on X. Instagram. TikTok."
            delay={0}
            layout={layout}
          />
          <Line
            text="I made demo videos."
            delay={16}
            color={colors.textMuted}
            layout={layout}
          />
          <Line text="I did everything right." delay={32} layout={layout} />
        </Act>
      </Sequence>

      {/* Act 2d — The result with gameplay video bg, red-tinted (frames 360–509) */}
      <Sequence from={360} durationInFrames={150}>
        <Act
          layout={layout}
          video={
            <OffthreadVideoClip
              src="bubble-war-2.mp4"
              startFrom={0}
              opacity={0.9}
              style={{ filter: "blur(12px) brightness(0.25) saturate(0.4) hue-rotate(320deg)" }}
            />
          }
        >
          <div
            style={{
              opacity: opacityIn(frame, 30),
              fontSize: layout.titleSize * 0.95,
              fontWeight: 600,
              color: colors.red,
              lineHeight: 1.2,
              textShadow: "0 0 50px rgba(224,92,59,0.45)",
            }}
          >
            But I didn't win.
          </div>
        </Act>
      </Sequence>

      {/* Act 2e — The insight (frames 510–659) */}
      <Sequence from={510} durationInFrames={150}>
        <Act layout={layout}>
          <div style={{ display: "flex", alignItems: "baseline", gap: 16 }}>
            <span
              style={{
                fontSize: layout.statSize,
                fontWeight: 600,
                color: colors.amber,
                lineHeight: 1,
                textShadow: "0 0 60px rgba(239,159,39,0.45)",
              }}
            >
              {countUp(frame, 0, 20, 1)}
            </span>
          </div>
          <Line
            text="visitor from the US checked my project."
            delay={24}
            color={colors.textMuted}
            layout={layout}
          />
          <Line
            text="The recap video included all the winners."
            delay={48}
            layout={layout}
          />
          <Line
            text="Before the announcement."
            delay={60}
            color={colors.textMuted}
            layout={layout}
          />
          <Line
            text="Was my project even considered?"
            delay={76}
            color={colors.textMuted}
            italic
            layout={layout}
          />
        </Act>
      </Sequence>
    </>
  );
};
