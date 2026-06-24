import React, { useMemo } from "react";
import { useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import { ThreeCanvas } from "@remotion/three";

type BubbleDef = {
  x: number;
  y: number;
  z: number;
  radius: number;
  speed: number;
  phase: number;
};

const N = 18;

function seededRandom(seed: number): number {
  const x = Math.sin(seed + 1) * 10000;
  return x - Math.floor(x);
}

export const BubbleField: React.FC<{ width: number; height: number }> = ({
  width,
  height,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const bubbles = useMemo<BubbleDef[]>(() => {
    return Array.from({ length: N }, (_, i) => ({
      x: (seededRandom(i * 7) - 0.5) * 14,
      y: (seededRandom(i * 13) - 0.5) * 8,
      z: seededRandom(i * 3) * -6,
      radius: 0.3 + seededRandom(i * 11) * 0.9,
      speed: 0.2 + seededRandom(i * 5) * 0.4,
      phase: seededRandom(i * 17) * Math.PI * 2,
    }));
  }, []);

  const overallOpacity = interpolate(frame, [0, fps * 0.5], [0, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <ThreeCanvas
      width={width}
      height={height}
      style={{ position: "absolute", inset: 0, opacity: overallOpacity * 0.35 }}
    >
      <ambientLight intensity={0.6} />
      <directionalLight position={[5, 8, 5]} intensity={0.8} />
      <pointLight position={[-5, -5, 3]} color="#EF9F27" intensity={0.8} />
      {bubbles.map((b, i) => {
        const t = frame / fps;
        const floatY = Math.sin(t * b.speed + b.phase) * 0.4;
        const floatX = Math.cos(t * b.speed * 0.7 + b.phase) * 0.2;
        return (
          <mesh
            key={i}
            position={[b.x + floatX, b.y + floatY, b.z]}
          >
            <sphereGeometry args={[b.radius, 20, 20]} />
            <meshPhysicalMaterial
              color="#C8AA7A"
              transparent
              opacity={0.08 + seededRandom(i * 19) * 0.07}
              roughness={0.2}
              metalness={0.15}
              transmission={0.85}
              thickness={1.2}
            />
          </mesh>
        );
      })}
    </ThreeCanvas>
  );
};
