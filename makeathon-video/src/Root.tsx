import React from "react";
import { Composition } from "remotion";
import { layout16x9, layout9x16 } from "./constants/layout";
import { MainSequence } from "./scenes/MainSequence";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="MakeathonStory16x9"
        component={() => <MainSequence layout={layout16x9} />}
        durationInFrames={1620}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="MakeathonStory9x16"
        component={() => <MainSequence layout={layout9x16} />}
        durationInFrames={1620}
        fps={30}
        width={1080}
        height={1920}
      />
    </>
  );
};
