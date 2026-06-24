# Copilot Instructions for Figma Makeathon Analysis

## Project Purpose

Scrape, aggregate, and analyze all publicly available data across 3 Figma × Contra makeathon editions to determine what separates winners from non-winners, with a focus on whether early posting is the dominant variable. Output is a data-backed community report published as a web page or interactive article.

The full project spec lives in `agents/context/prd.md` — read it before starting any implementation work.

## Tech Stack

- **Python** (primary language)
- **Playwright** for JavaScript-rendered page scraping (Contra community pages are JS-rendered — plain HTTP fetch won't work)
- **httpx** for static page fetches
- **pandas** for data wrangling and analysis
- **plotly** (or matplotlib/seaborn) for interactive charts
- **jinja2** or **mdx** for report generation

## Commands

```bash
# Setup
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Generate sample data (for testing without live scraping)
python generate_sample_data.py

# Full pipeline (scrape → analyze → report)
python main.py

# Individual phases
python scrape_winners.py    # Phase 1: winner deep-dive
python scrape_all.py        # Phase 2: all entries
python analyze.py           # Phase 3: analysis + charts + report
```

## Available Skills & MCP Servers

This project has domain-specific skills installed and MCP servers configured:

**Skills** (invoke with `skill` tool):
- `scrape` — General web scraping guidance and patterns
- `playwright-scraper` — Playwright-specific scraping workflows
- `pandas-data-analysis` — pandas data wrangling, aggregation, and analysis conventions
- `plotly` — Interactive chart generation with plotly
- `webapp-testing` — Playwright scripting patterns for browser automation

**MCP Servers** (configured in `.mcp.json`):
- `chrome-devtools-mcp` — Browser DevTools protocol for scraping JS-rendered pages (global)
- `playwright` — `@anthropic/mcp-server-playwright` for headless browser automation (project-level)

## Architecture

The project has three data phases, each producing artifacts consumed by the next:

1. **Phase 1 — Winners Deep Dive**: Scrape detailed metadata for each known winner (Contra post data, submission content URLs, social traction, recap inclusion). Output: structured per-winner data.

2. **Phase 2 — All Entries**: Scrape every post from each edition's Contra community topic page. Output: complete entry catalog with engagement metrics.

3. **Phase 3 — Computed Analysis**: Derive computed fields (`days_before_deadline`, `engagement_score`, `social_coverage`, `winner`) and run cross-entry statistical analysis (post timing distributions, correlation with winning, social presence comparisons).

Output deliverables:
- `winners.csv`, `all_entries.csv`, `social_posts.csv` — raw data
- Python analysis script/notebook with charts
- Markdown report → rendered as a web page

## Key Conventions

### Scraping

- Contra community pages require Playwright/Puppeteer — they are JavaScript-rendered, not static HTML.
- Contra post timestamps are relative ("3 days ago"). Resolve to absolute dates using the known submission window dates as anchor points in the PRD.
- If scraping YouTube video links, fetch `uploadDate` from the page `<meta>` or oEmbed API — this is key evidence for the "was the idea already done?" question.
- Rate-limit all scraping, respect robots.txt, add delays between requests.
- If Contra blocks scraping, fall back to browser automation with human-in-the-loop confirmation.

### Data Conventions

- `engagement_score` = likes + (comments × 2)
- `social_coverage` = count of distinct platforms linked
- `days_before_deadline` = how many days before the submission window close they posted
- All timestamps should be resolved to absolute dates before analysis.

### Three Known Editions

Refer to `agents/context/prd.md` for exact dates, prize pools, and known winner seed data. The Config Makeathon 2026 winners were to be announced live at Config on June 23 — scrape from `contra.com/community/topic/configmakeathon` and Figma/Contra social channels.

### Before Starting Any Implementation

Read `agents/context/prd.md` in full — it contains the complete data schema, all source URLs, seed winner data that must be completed/verified, and edge cases the agent must handle.
