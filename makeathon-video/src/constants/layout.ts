export interface Layout {
  width: number;
  height: number;
  titleSize: number;
  statSize: number;
  bodySize: number;
  smallSize: number;
  padding: number;
  maxWidth: number;
}

export const layout16x9: Layout = {
  width: 1920,
  height: 1080,
  titleSize: 80,
  statSize: 160,
  bodySize: 42,
  smallSize: 28,
  padding: 120,
  maxWidth: 1400,
};

export const layout9x16: Layout = {
  width: 1080,
  height: 1920,
  titleSize: 64,
  statSize: 130,
  bodySize: 36,
  smallSize: 24,
  padding: 80,
  maxWidth: 920,
};
