import React from "react";
import { AbsoluteFill, useCurrentFrame, Sequence } from "remotion";
import { colors } from "../constants/colors";
import type { Layout } from "../constants/layout";
import {
  countUp,
  countUpDecimal,
  opacityIn,
  barGrow,
  springIn,
} from "../components/animations";

export const Scene4_Data: React.FC<{ layout: Layout }> = ({ layout }) => {
  return (
    <>
      <Sequence from={0} durationInFrames={180}>
        <DataTiming layout={layout} />
      </Sequence>
      <Sequence from={180} durationInFrames={150}>
        <DataEngagement layout={layout} />
      </Sequence>
      <Sequence from={330} durationInFrames={150}>
        <DataCrossposting layout={layout} />
      </Sequence>
      <Sequence from={480} durationInFrames={120}>
        <DataVideoDates layout={layout} />
      </Sequence>
    </>
  );
};

const DataTiming: React.FC<{ layout: Layout }> = ({ layout }) => {
  const frame = useCurrentFrame();
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
          fontSize: layout.bodySize,
          fontWeight: 500,
          color: colors.textMuted,
          opacity: opacityIn(frame, 0),
          marginBottom: 40,
        }}
      >
        When did winners post?
      </div>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: 24,
          width: "100%",
          maxWidth: layout.maxWidth,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <span
            style={{
              width: layout.padding * 1.2,
              fontSize: layout.smallSize,
              fontWeight: 500,
              color: colors.textMuted,
              textAlign: "right",
              flexShrink: 0,
            }}
          >
            Non-winners
          </span>
          <div
            style={{
              flex: 1,
              height: 36,
              backgroundColor: colors.border,
              borderRadius: 6,
              overflow: "hidden",
            }}
          >
            <div
              style={{
                height: "100%",
                width: `${(11.7 / 14) * 100 * barGrow(frame, 10, 30)}%`,
                backgroundColor: colors.gray,
                borderRadius: 6,
              }}
            />
          </div>
          <span
            style={{
              width: 120,
              fontSize: layout.bodySize * 0.8,
              fontWeight: 500,
              color: colors.gray,
              opacity: opacityIn(frame, 35),
              flexShrink: 0,
            }}
          >
            Day {countUpDecimal(frame, 35, 12, 11.7, 1)}
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <span
            style={{
              width: layout.padding * 1.2,
              fontSize: layout.smallSize,
              fontWeight: 500,
              color: colors.textPrimary,
              textAlign: "right",
              flexShrink: 0,
            }}
          >
            Winners
          </span>
          <div
            style={{
              flex: 1,
              height: 40,
              backgroundColor: colors.border,
              borderRadius: 6,
              overflow: "hidden",
            }}
          >
            <div
              style={{
                height: "100%",
                width: `${(4.4 / 14) * 100 * barGrow(frame, 20, 30)}%`,
                backgroundColor: colors.teal,
                borderRadius: 6,
              }}
            />
          </div>
          <span
            style={{
              width: 120,
              fontSize: layout.bodySize * 0.8,
              fontWeight: 500,
              color: colors.teal,
              opacity: opacityIn(frame, 45),
              flexShrink: 0,
            }}
          >
            Day {countUpDecimal(frame, 45, 12, 4.4, 1)}
          </span>
        </div>
      </div>
      <div
        style={{
          marginTop: 48,
          fontSize: layout.titleSize * 0.7,
          fontWeight: 600,
          color: colors.amber,
          opacity: opacityIn(frame, 60),
          transform: `translateY(${Math.max(0, 40 - springIn(frame, 60) * 40)}px)`,
        }}
      >
        A full week earlier.
      </div>
    </AbsoluteFill>
  );
};

const DataEngagement: React.FC<{ layout: Layout }> = ({ layout }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill
      style={{
        backgroundColor: colors.bg,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        fontFamily: '"Inter", sans-serif',
      }}
    >
      <div
        style={{
          fontSize: layout.statSize,
          fontWeight: 600,
          color: colors.amber,
          lineHeight: 1,
          opacity: opacityIn(frame, 0),
        }}
      >
        {countUpDecimal(frame, 0, 20, 8.7, 1)}x
      </div>
      <div
        style={{
          fontSize: layout.smallSize,
          fontWeight: 500,
          color: colors.textMuted,
          marginTop: 16,
          opacity: opacityIn(frame, 20),
        }}
      >
        more engagement. winners vs non-winners.
      </div>
      <div
        style={{
          fontSize: layout.bodySize,
          fontWeight: 500,
          color: colors.textPrimary,
          marginTop: 40,
          opacity: opacityIn(frame, 40),
        }}
      >
        They weren't just better.
      </div>
      <div
        style={{
          fontSize: layout.bodySize,
          fontWeight: 500,
          color: colors.amber,
          marginTop: 8,
          opacity: opacityIn(frame, 50),
        }}
      >
        They were louder, earlier.
      </div>
    </AbsoluteFill>
  );
};

const DataCrossposting: React.FC<{ layout: Layout }> = ({ layout }) => {
  const frame = useCurrentFrame();
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
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          gap: layout.padding,
          flexWrap: "wrap",
        }}
      >
        <div style={{ textAlign: "center", opacity: opacityIn(frame, 0) }}>
          <div
            style={{
              fontSize: layout.smallSize,
              fontWeight: 500,
              color: colors.textPrimary,
              marginBottom: 16,
            }}
          >
            Winners
          </div>
          <div
            style={{
              fontSize: layout.statSize,
              fontWeight: 600,
              color: colors.teal,
              lineHeight: 1,
            }}
          >
            {countUpDecimal(frame, 10, 15, 3.0, 1)}
          </div>
          <div
            style={{
              fontSize: layout.smallSize,
              fontWeight: 500,
              color: colors.textMuted,
              marginTop: 8,
            }}
          >
            platforms
          </div>
        </div>
        <div style={{ textAlign: "center", opacity: opacityIn(frame, 8) }}>
          <div
            style={{
              fontSize: layout.smallSize,
              fontWeight: 500,
              color: colors.textMuted,
              marginBottom: 16,
            }}
          >
            Non-winners
          </div>
          <div
            style={{
              fontSize: layout.statSize,
              fontWeight: 600,
              color: colors.gray,
              lineHeight: 1,
            }}
          >
            {countUpDecimal(frame, 18, 15, 1.1, 1)}
          </div>
          <div
            style={{
              fontSize: layout.smallSize,
              fontWeight: 500,
              color: colors.textMuted,
              marginTop: 8,
            }}
          >
            platforms
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

const DataVideoDates: React.FC<{ layout: Layout }> = ({ layout }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill
      style={{
        backgroundColor: colors.bg,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: `0 ${layout.padding}px`,
        fontFamily: '"Inter", sans-serif',
      }}
    >
      <div
        style={{
          fontSize: layout.bodySize,
          fontWeight: 500,
          color: colors.textPrimary,
          opacity: opacityIn(frame, 0),
          textAlign: "center",
        }}
      >
        We checked the video upload dates.
      </div>
      <div
        style={{
          fontSize: layout.bodySize,
          fontWeight: 500,
          color: colors.amber,
          marginTop: 32,
          opacity: opacityIn(frame, 25),
          textAlign: "center",
        }}
      >
        No winner started before the challenge opened.
      </div>
      <div
        style={{
          fontSize: layout.bodySize,
          fontWeight: 500,
          color: colors.textPrimary,
          marginTop: 40,
          opacity: opacityIn(frame, 50),
          textAlign: "center",
        }}
      >
        The advantage wasn't preparation.
      </div>
      <div
        style={{
          fontSize: layout.bodySize,
          fontWeight: 500,
          color: colors.amber,
          marginTop: 8,
          opacity: opacityIn(frame, 60),
          textAlign: "center",
        }}
      >
        It was early, loud execution.
      </div>
    </AbsoluteFill>
  );
};
