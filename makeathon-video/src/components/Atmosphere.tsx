import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate } from "remotion";

/**
 * Animated film grain. Driven by useCurrentFrame (the feTurbulence `seed`
 * changes each frame), so the grain shimmers like real film. mixBlendMode
 * "overlay" keeps shadows near-black while texturing the midtones.
 */
export const FilmGrain: React.FC<{ opacity?: number }> = ({ opacity = 0.1 }) => {
  const frame = useCurrentFrame();
  const seed = frame % 73;
  return (
    <AbsoluteFill
      style={{
        pointerEvents: "none",
        mixBlendMode: "overlay",
        opacity,
        zIndex: 40,
      }}
    >
      <svg width="100%" height="100%" style={{ position: "absolute", inset: 0 }}>
        <filter id="filmGrain">
          <feTurbulence
            type="fractalNoise"
            baseFrequency="0.9"
            numOctaves={2}
            seed={seed}
            stitchTiles="stitch"
          />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter="url(#filmGrain)" />
      </svg>
    </AbsoluteFill>
  );
};

/** Radial vignette — darkens the edges to pull the eye to center. */
export const Vignette: React.FC<{ strength?: number }> = ({ strength = 0.6 }) => (
  <AbsoluteFill
    style={{
      pointerEvents: "none",
      zIndex: 41,
      background: `radial-gradient(ellipse at center, transparent 42%, rgba(0,0,0,${strength}) 100%)`,
    }}
  />
);

/** Cinematic letterbox bars — wider crop for 16:9, gentle frame for 9:16. */
export const Letterbox: React.FC = () => {
  const { width, height } = useVideoConfig();
  const bar = width > height ? height * 0.07 : height * 0.04;
  const barStyle: React.CSSProperties = {
    position: "absolute",
    left: 0,
    right: 0,
    height: bar,
    backgroundColor: "#000",
    zIndex: 49,
    pointerEvents: "none",
  };
  return (
    <>
      <div style={{ ...barStyle, top: 0 }} />
      <div style={{ ...barStyle, bottom: 0 }} />
    </>
  );
};

/**
 * Full atmosphere stack laid over all scenes. Also adds a brief opening
 * "fade from black" and a closing fade so the piece bookends like a trailer.
 */
export const Atmosphere: React.FC<{ totalFrames: number }> = ({ totalFrames }) => {
  const frame = useCurrentFrame();
  const openFade = interpolate(frame, [0, 18], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const closeFade = interpolate(
    frame,
    [totalFrames - 16, totalFrames - 1],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const blackout = Math.max(openFade, closeFade);
  return (
    <>
      <Vignette />
      <FilmGrain />
      <Letterbox />
      <AbsoluteFill
        style={{
          pointerEvents: "none",
          backgroundColor: "#000",
          opacity: blackout,
          zIndex: 60,
        }}
      />
    </>
  );
};
