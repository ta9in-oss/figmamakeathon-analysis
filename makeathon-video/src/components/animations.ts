import { interpolate, spring, Easing } from "remotion";

export function fadeSlideY(frame: number, delay: number = 0, distance: number = 24): number {
  const active = frame - delay;
  const opacity = interpolate(active, [0, 8], [0, 1], { extrapolateRight: "clamp" });
  const y = interpolate(active, [0, 12], [distance, 0], {
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  return opacity * 1000 + y; // hack: return both packed, unpack in component
}

export function opacityIn(frame: number, delay: number = 0): number {
  return interpolate(frame - delay, [0, 10], [0, 1], { extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
}

export function countUp(frame: number, delay: number, duration: number, target: number): number {
  const active = frame - delay;
  return Math.round(interpolate(active, [0, duration], [0, target], {
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  }));
}

export function countUpDecimal(frame: number, delay: number, duration: number, target: number, decimals: number = 1): string {
  const active = frame - delay;
  const val = interpolate(active, [0, duration], [0, target], {
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  return val.toFixed(decimals);
}

export function springIn(frame: number, delay: number = 0): number {
  return spring({ frame: frame - delay, fps: 30, config: { damping: 14, stiffness: 120 } });
}

export function slideFromRight(frame: number, delay: number = 0): number {
  const active = frame - delay;
  return interpolate(active, [0, 25], [200, 0], {
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
}

export function barGrow(frame: number, delay: number, duration: number): number {
  const active = frame - delay;
  return interpolate(active, [0, duration], [0, 1], {
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
}

// Slow cinematic dolly: scale drifts up over the scene for a "push-in" feel.
export function pushIn(
  frame: number,
  duration: number,
  from: number = 1,
  to: number = 1.06
): number {
  return interpolate(frame, [0, duration], [from, to], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad),
  });
}

// Slow, weighted entrance — rises further and eases longer than opacityIn,
// for the dramatic doc-trailer reveal rhythm. Returns {opacity, y}.
export function dramaIn(
  frame: number,
  delay: number = 0,
  distance: number = 40
): { opacity: number; y: number } {
  const active = frame - delay;
  const opacity = interpolate(active, [0, 18], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const y = interpolate(active, [0, 24], [distance, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  return { opacity, y };
}
