import React from "react";
import { Series } from "remotion";
import type { Layout } from "../constants/layout";
import { Scene1_Hook } from "./Scene1_Hook";
import { Scene2_PersonalStory } from "./Scene2_PersonalStory";
import { Scene3_Pivot } from "./Scene3_Pivot";
import { Scene4_Data } from "./Scene4_Data";
import { Scene5_Formula } from "./Scene5_Formula";
import { Scene6_Close } from "./Scene6_Close";

export const MainSequence: React.FC<{ layout: Layout }> = ({ layout }) => {
  return (
    <Series>
      <Series.Sequence durationInFrames={90}>
        <Scene1_Hook layout={layout} />
      </Series.Sequence>
      <Series.Sequence durationInFrames={660}>
        <Scene2_PersonalStory layout={layout} />
      </Series.Sequence>
      <Series.Sequence durationInFrames={90}>
        <Scene3_Pivot layout={layout} />
      </Series.Sequence>
      <Series.Sequence durationInFrames={600}>
        <Scene4_Data layout={layout} />
      </Series.Sequence>
      <Series.Sequence durationInFrames={120}>
        <Scene5_Formula layout={layout} />
      </Series.Sequence>
      <Series.Sequence durationInFrames={120}>
        <Scene6_Close layout={layout} />
      </Series.Sequence>
    </Series>
  );
};
