"""Project configuration — edition dates, URLs, known winner seed data."""

from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional

# ── Edition definitions ────────────────────────────────────────────────────

@dataclass
class Edition:
    name: str
    start_date: datetime
    end_date: datetime
    prize_pool: str
    topic_url: str
    topic_slug: str
    hashtag: str
    winner_seed: list[dict] = field(default_factory=list)


EDITIONS = [
    Edition(
        name="Figma Make-a-thon (Sep 2025)",
        start_date=datetime(2025, 9, 3),
        end_date=datetime(2025, 9, 10),
        prize_pool="$100K",
        topic_url="https://contra.com/community/topic/figmamakeathon",
        topic_slug="figmamakeathon",
        hashtag="#figmamakeathon",
        winner_seed=[
            {"place": "1st ($50K)", "project": "Web Poetry", "creator": "Cara Ellis", "contra_url": None},
            {"place": "2nd ($15K)", "project": None, "creator": None, "contra_url": None},
            {"place": "3rd ($7.5K)", "project": "Plan That Trip. Now", "creator": "Johannes Specht", "contra_url": None},
            {"place": "Most Creative", "project": None, "creator": None, "contra_url": None},
            {"place": "Most Innovative", "project": "Package Customizer", "creator": "Daniella Marynova & Max Pradella", "contra_url": None},
            {"place": "Best Prompt", "project": None, "creator": None, "contra_url": None},
        ],
    ),
    Edition(
        name="Figma Makeathon March 2026",
        start_date=datetime(2026, 2, 1),
        end_date=datetime(2026, 3, 16),
        prize_pool="$100K",
        topic_url="https://contra.com/community/topic/figmamakeathonmarch2026",
        topic_slug="figmamakeathonmarch2026",
        hashtag="#figmamakeathonmarch2026",
        winner_seed=[
            {"place": "Best Overall", "project": "Common Thread", "creator": "Charlota Blunárová", "contra_url": "https://figma.bot/476bnit"},
            {"place": "Excellence in Craft", "project": "TOKYO", "creator": "Kiel Cole", "contra_url": "https://figma.bot/479fyKm"},
            {"place": "New Interaction", "project": "Pucker", "creator": "Aleyna Çatak", "contra_url": "https://figma.bot/417D3jl"},
            {"place": "Boundary Pushing", "project": "Airwwave", "creator": "Lee Black", "contra_url": "https://figma.bot/4lyJSnm"},
            {"place": "Reimagining Iconic Interactions", "project": "Duet Booth", "creator": "Paige Latimer", "contra_url": "https://figma.bot/4bpSesV"},
            {"place": "Fan Favorite on Social", "project": "Reframe It", "creator": "Dann Petty", "contra_url": "https://figma.bot/4lzmkyJ"},
        ],
    ),
    Edition(
        name="Config Makeathon 2026",
        start_date=datetime(2026, 6, 4),
        end_date=datetime(2026, 6, 18),
        prize_pool="$100K",
        topic_url="https://contra.com/community/topic/configmakeathon",
        topic_slug="configmakeathon",
        hashtag="#configmakeathon",
        winner_seed=[],  # Winners to be scraped post-announcement
    ),
]

# ── External reference URLs ─────────────────────────────────────────────────

FIGMA_BLOG_URL = "https://www.figma.com/blog/6-winning-figma-makes-and-what-you-can-learn-from-them/"
CONTRA_RECAP_SEP2025 = "https://contra.com/community/neIDybLs-explore-the-innovative-winners-of-figmas"
CONTRA_RECAP_MAR2026 = "https://contra.com/community/6OZFlCWv-explore-projects-from-figma-makeathon-challenges"
CONFIG_EVENT_URL = "https://config.figma.com/san-francisco/event/52f50783-e30a-4a98-9039-fab3d9f04fa4/"
LUMA_SEP2025 = "https://luma.com/z3s4o6g8"
FIGMA_X_WINNERS_TWEET = "https://x.com/figma/status/1968007805203517458"

# ── Scraping settings ───────────────────────────────────────────────────────

REQUEST_DELAY_SECONDS = 2.0
PLAYWRIGHT_TIMEOUT_MS = 30_000
PAGE_LOAD_WAIT_MS = 5_000
