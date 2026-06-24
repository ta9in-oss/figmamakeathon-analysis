import { loadFont } from "@remotion/google-fonts/Inter";
import { useEffect } from "react";

const { waitUntilDone } = loadFont("normal", {
  subsets: ["latin"],
  weights: ["400", "500", "600"],
});

export const useInterFont = () => {
  return waitUntilDone;
};
