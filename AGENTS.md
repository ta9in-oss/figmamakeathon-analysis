# AGENTS.md — Figma Makeathon Analysis

## Overview
Two-project monorepo analyzing Figma x Contra makeathon data to determine what separates winners from non-winners.

## Projects

### `python/` — Data Pipeline
Scraping and analysis pipeline. Python 3.12+ with playwright, pandas, plotly.

```bash
cd python && source venv/bin/activate
python generate_sample_data.py   # test with synthetic data
python main.py                    # full pipeline: scrape -> analyze -> report
python analyze.py                 # analysis + charts from existing CSVs
python check_video_dates.py       # winner video upload date investigation
```

**Key files:** `src/scraper.py` (Playwright-based Contra scraper), `src/analysis.py` (pandas + plotly), `src/models.py` (Entry/SocialPost/AnalysisResult dataclasses), `src/config.py` (edition definitions, URLs).

### `astro/` — Presentation Site
AstroJS + Tailwind + React. pnpm. Deployed to Cloudflare Pages.

```bash
cd astro && pnpm install && pnpm dev
pnpm build   # outputs to dist/
```

**Pages:** `/` (home), `/report` (full report), `/charts` (interactive plotly iframes), `/data` (CSV downloads + schema), `/video-analysis` (winner video investigation).

## Deployment
- **GitHub:** `ta9in-oss/figmamakeathon-analysis`
- **Production:** `figmamakeathon-analysis.pages.dev`
- **Custom domain:** `figmamakeathon.ta9in.com` (pending DNS)
- **Deploy command:** `cd astro && pnpm build && npx wrangler pages deploy dist --project-name=figmamakeathon-analysis --branch=main`

## Conventions
- No emojis. Clean minimal dark design. Purple (#7C3AED) accent.
- Python: use virtual env, type hints throughout.
- Data: CSV output with datetime ISO 8601. `engagement_score` = likes + (comments x 2).
- Charts: plotly HTML saved to `output/figures/`, served as iframes.
- Always read `agents/context/prd.md` before starting work.
