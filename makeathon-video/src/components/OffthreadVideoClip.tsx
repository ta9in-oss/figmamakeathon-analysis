import React from "react";
import { OffthreadVideo } from "@remotion/media";
import { staticFile } from "remotion";

export const OffthreadVideoClip: React.FC<{
  src: string;
  startFrom?: number;
  opacity?: number;
  style?: React.CSSProperties;
}> = ({ src, startFrom = 0, opacity = 1, style }) => {
  return (
    <OffthreadVideo
      src={staticFile(src)}
      startFrom={startFrom}
      muted
      style={{
        position: "absolute",
        inset: 0,
        width: "100%",
        height: "100%",
        objectFit: "cover",
        opacity,
        filter: "blur(12px) brightness(0.35) saturate(1.4)",
        ...style,
      }}
    />
  );
};
