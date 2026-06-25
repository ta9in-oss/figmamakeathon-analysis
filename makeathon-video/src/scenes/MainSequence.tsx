import React from "react";
import { AbsoluteFill } from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import type { Layout } from "../constants/layout";
import { colors } from "../constants/colors";
import { Atmosphere } from "../components/Atmosphere";
import { Scene1_Hook } from "./Scene1_Hook";
import { Scene2_PersonalStory } from "./Scene2_PersonalStory";
import { Scene3_Pivot } from "./Scene3_Pivot";
import { Scene4_Data } from "./Scene4_Data";
import { Scene5_Formula } from "./Scene5_Formula";
import { Scene6_Close } from "./Scene6_Close";

const TRANSITION = linearTiming({ durationInFrames: 15 });
const TOTAL_FRAMES = 1605;

export const MainSequence: React.FC<{ layout: Layout }> = ({ layout }) => {
  return (
    <AbsoluteFill style={{ backgroundColor: colors.bg }}>
      <TransitionSeries>
        <TransitionSeries.Sequence durationInFrames={90}>
          <Scene1_Hook layout={layout} />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={fade()} timing={TRANSITION} />

        <TransitionSeries.Sequence durationInFrames={660}>
          <Scene2_PersonalStory layout={layout} />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={fade()} timing={TRANSITION} />

        <TransitionSeries.Sequence durationInFrames={90}>
          <Scene3_Pivot layout={layout} />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={fade()} timing={TRANSITION} />

        <TransitionSeries.Sequence durationInFrames={600}>
          <Scene4_Data layout={layout} />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={fade()} timing={TRANSITION} />

        <TransitionSeries.Sequence durationInFrames={120}>
          <Scene5_Formula layout={layout} />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={fade()} timing={TRANSITION} />

        <TransitionSeries.Sequence durationInFrames={120}>
          <Scene6_Close layout={layout} />
        </TransitionSeries.Sequence>
      </TransitionSeries>

      <Atmosphere totalFrames={TOTAL_FRAMES} />
    </AbsoluteFill>
  );
};
