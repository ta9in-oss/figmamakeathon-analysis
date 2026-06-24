import React from "react";
import {
  AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate,
  spring, Sequence, Audio,
} from "remotion";

// ── Color system ──
const BG = "#1A1916";
const TEXT = "#F7F5F0";
const AMBER = "#EF9F27";
const TEAL = "#1D9E75";
const GRAY = "#5F5E5A";
const GRID = "#2C2C2A";

interface Props { format: "16:9" | "9:16"; }

const TitleText: React.FC<{ text: string; delay?: number }> = ({ text, delay = 0 }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame - delay, [0, 15], [0, 1], { extrapolateRight: "clamp" });
  const y = spring({ frame: frame - delay, fps: 60, config: { damping: 20, stiffness: 80 } }) * 40 - 40;
  return (
    <div style={{ opacity, transform: `translateY(${y}px)`, fontSize: 72, fontWeight: 500, color: TEXT, lineHeight: 1.15, textAlign: "center" }}>
      {text}
    </div>
  );
};

const StatText: React.FC<{ value: string; label: string; color?: string }> = ({ value, label, color = AMBER }) => {
  const frame = useCurrentFrame();
  const scale = spring({ frame, fps: 60, config: { damping: 12, stiffness: 100 } });
  return (
    <div style={{ textAlign: "center" }}>
      <div style={{ fontSize: 96, fontWeight: 500, color, lineHeight: 1.1, transform: `scale(${scale})` }}>{value}</div>
      <div style={{ fontSize: 28, color: GRAY, marginTop: 12 }}>{label}</div>
    </div>
  );
};

const Scene: React.FC<{ children: React.ReactNode; bg?: string }> = ({ children, bg = BG }) => (
  <AbsoluteFill style={{ backgroundColor: bg, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: 80 }}>
    {children}
  </AbsoluteFill>
);

export const MakeathonStory: React.FC<Props> = ({ format }) => {
  const frame = useCurrentFrame();
  const isWide = format === "16:9";
  const scale = isWide ? 1 : 0.6;

  // Scene timings (in frames at 60fps)
  const scenes = {
    hook: { start: 0, end: 180 },
    intro: { start: 180, end: 480 },
    failure: { start: 480, end: 780 },
    realization: { start: 780, end: 1080 },
    scrape: { start: 1080, end: 1320 },
    data1: { start: 1320, end: 1740 },
    data2: { start: 1740, end: 2160 },
    data3: { start: 2160, end: 2580 },
    data4: { start: 2580, end: 2940 },
    conclusion: { start: 2940, end: 3300 },
    cta: { start: 3300, end: 3600 },
  };

  return (
    <div style={{ flex: 1, backgroundColor: BG, fontFamily: "Inter, -apple-system, sans-serif", transform: `scale(${scale})`, transformOrigin: "center center", width: 1920, height: 1080 }}>
      
      {/* Scene 1: Hook */}
      <Sequence from={scenes.hook.start} durationInFrames={scenes.hook.end - scenes.hook.start}>
        <Scene>
          <div style={{ fontSize: 64, fontWeight: 500, color: AMBER, lineHeight: 1.1, textAlign: "center", maxWidth: 1200 }}>
            How to <span style={{ color: TEAL }}>actually</span> win a<br />Figma Makeathon?
          </div>
        </Scene>
      </Sequence>

      {/* Scene 2: Personal intro */}
      <Sequence from={scenes.intro.start} durationInFrames={scenes.intro.end - scenes.intro.start}>
        <Scene>
          <TitleText text="I created Bubble War" delay={0} />
          <div style={{ marginTop: 40, fontSize: 32, color: GRAY }}>and I was sure it would win.</div>
        </Scene>
      </Sequence>

      {/* Scene 3: What I did */}
      <Sequence from={scenes.failure.start} durationInFrames={scenes.failure.end - scenes.failure.start}>
        <Scene>
          <div style={{ fontSize: 36, color: TEXT, lineHeight: 1.8, textAlign: "center", maxWidth: 1000 }}>
            <div>Published my entry <span style={{ color: AMBER }}>13 hours</span> before the deadline.</div>
            <div>Shared it to X, Instagram, and TikTok.</div>
            <div>Created a video to showcase the process.</div>
            <div style={{ marginTop: 60, fontSize: 48, color: TEAL }}>But I didn't win.</div>
          </div>
        </Scene>
      </Sequence>

      {/* Scene 4: Realization */}
      <Sequence from={scenes.realization.start} durationInFrames={scenes.realization.end - scenes.realization.start}>
        <Scene>
          <div style={{ fontSize: 36, color: TEXT, lineHeight: 1.8, textAlign: "center", maxWidth: 1000 }}>
            <div>Only <span style={{ color: AMBER }}>one user</span> checked the project.</div>
            <div style={{ marginTop: 30, color: GRAY }}>The recap video featured all the winners beforehand.</div>
            <div style={{ marginTop: 30, color: GRAY }}>Maybe my entry was never really considered.</div>
          </div>
        </Scene>
      </Sequence>

      {/* Scene 5: The investigation */}
      <Sequence from={scenes.scrape.start} durationInFrames={scenes.scrape.end - scenes.scrape.start}>
        <Scene>
          <div style={{ fontSize: 48, color: TEXT, textAlign: "center", maxWidth: 1000 }}>
            <span style={{ color: AMBER }}>So I scraped</span> every entry.<br />
            <span style={{ color: GRAY }}>From every makeathon.</span>
          </div>
        </Scene>
      </Sequence>

      {/* Scene 6: Data reveal 1 - Timing */}
      <Sequence from={scenes.data1.start} durationInFrames={scenes.data1.end - scenes.data1.start}>
        <Scene>
          <StatText value="Day 4.4" label="Average post day for winners" color={TEAL} />
          <div style={{ marginTop: 40 }}>
            <StatText value="Day 11.7" label="Average post day for non-winners" color={GRAY} />
          </div>
          <div style={{ marginTop: 60, fontSize: 28, color: AMBER }}>Winners posted 7.3 days earlier.</div>
        </Scene>
      </Sequence>

      {/* Scene 7: Data reveal 2 - Engagement */}
      <Sequence from={scenes.data2.start} durationInFrames={scenes.data2.end - scenes.data2.start}>
        <Scene>
          <StatText value="8.7x" label="More engagement for winners" color={TEAL} />
          <div style={{ marginTop: 60, fontSize: 28, color: TEXT }}>
            <span style={{ color: AMBER }}>3.0</span> platforms vs <span style={{ color: GRAY }}>1.1</span> for non-winners.
          </div>
        </Scene>
      </Sequence>

      {/* Scene 8: Data reveal 3 - Recaps */}
      <Sequence from={scenes.data3.start} durationInFrames={scenes.data3.end - scenes.data3.start}>
        <Scene>
          <StatText value="82.6%" label="Winners in official recaps" color={TEAL} />
          <div style={{ marginTop: 40 }}>
            <StatText value="4.1%" label="Non-winners in official recaps" color={GRAY} />
          </div>
        </Scene>
      </Sequence>

      {/* Scene 9: Data reveal 4 - No pre-work */}
      <Sequence from={scenes.data4.start} durationInFrames={scenes.data4.end - scenes.data4.start}>
        <Scene>
          <div style={{ fontSize: 48, color: TEXT, textAlign: "center", maxWidth: 1000 }}>
            Zero evidence of<br />
            <span style={{ color: TEAL }}>pre-challenge</span> work.
          </div>
          <div style={{ marginTop: 40, fontSize: 28, color: GRAY }}>
            The advantage is <span style={{ color: AMBER }}>early submissions</span>, not early starts.
          </div>
        </Scene>
      </Sequence>

      {/* Scene 10: Conclusion */}
      <Sequence from={scenes.conclusion.start} durationInFrames={scenes.conclusion.end - scenes.conclusion.start}>
        <Scene>
          <div style={{ fontSize: 36, color: TEXT, lineHeight: 1.8, textAlign: "center", maxWidth: 1000 }}>
            <div><span style={{ color: AMBER }}>Post early.</span></div>
            <div><span style={{ color: AMBER }}>Cross-post everywhere.</span></div>
            <div><span style={{ color: AMBER }}>Include a video demo.</span></div>
            <div><span style={{ color: AMBER }}>Build in public.</span></div>
            <div style={{ marginTop: 40, color: TEAL }}>That's how you win.</div>
          </div>
        </Scene>
      </Sequence>

      {/* Scene 11: CTA */}
      <Sequence from={scenes.cta.start} durationInFrames={scenes.cta.end - scenes.cta.start}>
        <Scene>
          <div style={{ fontSize: 36, color: TEXT, textAlign: "center", maxWidth: 1000 }}>
            <div style={{ color: GRAY }}>Full analysis and raw data at</div>
            <div style={{ marginTop: 20, fontSize: 48, color: AMBER }}>figmamakeathon.ta9in.com</div>
            <div style={{ marginTop: 40, fontSize: 24, color: GRAY }}>github.com/ta9in-oss/figmamakeathon-analysis</div>
          </div>
        </Scene>
      </Sequence>

    </div>
  );
};
