import { Composition } from "remotion";
import { MakeathonStory } from "./compositions/MakeathonStory";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="MakeathonStory-16x9"
        component={MakeathonStory}
        durationInFrames={3600} // 60 seconds at 60fps
        fps={60}
        width={1920}
        height={1080}
        defaultProps={{ format: "16:9" }}
      />
      <Composition
        id="MakeathonStory-9x16"
        component={MakeathonStory}
        durationInFrames={3600}
        fps={60}
        width={1080}
        height={1920}
        defaultProps={{ format: "9:16" }}
      />
    </>
  );
};
