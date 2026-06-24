#!/usr/bin/env python3
"""Generate realistic sample data for testing the analysis pipeline without live scraping.

Models the PRD's key hypotheses:
- Winners tend to post earlier in the submission window
- Early posters get more engagement (longer visibility window)
- Winners have higher social presence (more platforms)
- Winners are heavily favored in official recaps
- Higher follower counts correlate with higher engagement
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path
import math

from src.config import EDITIONS
from src.models import Entry


def _posting_day_beta(is_winner: bool, window_days: int) -> int:
    """Generate a posting day using a beta distribution.
    Winners strongly cluster in the first 30% of the window;
    non-winners spread across the full window with a slight deadline skew.
    """
    if is_winner:
        # ~80% of winners post in first 30% of window
        raw = random.betavariate(alpha=1.5, beta=6.0)
    else:
        # Non-winners: roughly uniform with slight deadline bias
        raw = random.betavariate(alpha=1.2, beta=0.9)
    day = max(1, min(window_days, int(raw * window_days) + 1))
    return day


def _social_platforms(is_winner: bool) -> tuple[int, bool, bool, bool, bool, bool]:
    """Generate realistic cross-posting data. Winners cross-post to more platforms."""
    if is_winner:
        base_prob = 0.75  # High probability per platform
    else:
        base_prob = 0.30

    x = random.random() < base_prob
    linkedin = random.random() < base_prob * 0.8
    instagram = random.random() < base_prob * 0.7
    threads = random.random() < base_prob * 0.5
    bluesky = random.random() < base_prob * 0.4

    count = sum([x, linkedin, instagram, threads, bluesky])
    return count, x, linkedin, instagram, threads, bluesky


def generate_sample_entries() -> list[Entry]:
    """Generate sample entries that mirror expected real-world patterns."""
    entries = []
    entry_id = 0
    winner_names = [
        "Web Poetry", "Plan That Trip. Now", "Package Customizer",
        "Common Thread", "TOKYO", "Pucker", "Airwwave",
        "Duet Booth", "Reframe It", "Pixel Flow", "Color Bloom",
        "Type Forge", "Motion Study", "Grid Garden", "Wave Form",
    ]
    creator_names = [
        "Cara Ellis", "Johannes Specht", "Daniella Marynova",
        "Charlota Blunárová", "Kiel Cole", "Aleyna Çatak",
        "Lee Black", "Paige Latimer", "Dann Petty",
        "Alex Rivera", "Mia Chen", "Sam Okafor",
        "Nina Petrov", "Diego Ramirez", "Yuki Tanaka",
    ]

    for edition in EDITIONS:
        window_days = (edition.end_date - edition.start_date).days
        # Scale entries to edition duration
        num_entries = random.randint(80, 120)
        # 6-8% win rate per edition
        num_winners = max(5, min(10, int(num_entries * 0.08)))
        winner_indices = set(random.sample(range(num_entries), num_winners))

        for i in range(num_entries):
            entry_id += 1
            is_winner = i in winner_indices

            posted_day = _posting_day_beta(is_winner, window_days)
            posted_at = edition.start_date + timedelta(days=posted_day - 1)

            # Base engagement decays with posting day (earlier = more time to accumulate)
            base_engagement = max(5, 400 * math.exp(-posted_day / (window_days * 0.4)))

            if is_winner:
                likes = int(random.gauss(base_engagement * 2.5, base_engagement * 0.5))
                comments = int(random.gauss(base_engagement * 0.4, base_engagement * 0.15))
                followers = int(random.gauss(2500, 1200))
                social_count, x, li, ig, th, bs = _social_platforms(True)
                in_recap = random.random() < 0.85
                in_blog = random.random() < 0.70
                video = random.random() < 0.85
                live = random.random() < 0.95
                figma_comm = random.random() < 0.85
            else:
                likes = int(random.gauss(base_engagement * 0.6, base_engagement * 0.3))
                comments = int(random.gauss(base_engagement * 0.1, base_engagement * 0.08))
                followers = int(random.gauss(400, 350))
                social_count, x, li, ig, th, bs = _social_platforms(False)
                in_recap = random.random() < 0.04
                in_blog = random.random() < 0.02
                video = random.random() < 0.50
                live = random.random() < 0.65
                figma_comm = random.random() < 0.40

            # Clamp non-negatives
            likes = max(0, likes)
            comments = max(0, comments)
            followers = max(0, followers)

            # Pick winner category and names from seeds or generated
            if is_winner and edition.winner_seed:
                cat = random.choice(edition.winner_seed)["place"]
            elif is_winner:
                cat = random.choice([
                    "Best Overall", "Excellence in Craft", "Most Innovative",
                ])
            else:
                cat = ""

            proj_name = random.choice(winner_names) if is_winner else f"Project {entry_id}"
            creator = random.choice(creator_names) if is_winner else f"Creator {entry_id}"

            entry = Entry(
                edition=edition.name,
                entry_id=f"entry_{entry_id:04d}",
                contra_url=f"https://contra.com/community/post/entry-{entry_id:04d}",
                posted_at=posted_at,
                day_relative_to_open=posted_day,
                days_before_deadline=window_days - posted_day,
                project_title=proj_name,
                creator_name=creator,
                live_url=(f"https://figma.site/sample-{entry_id}" if live else None),
                figma_community_url=(f"https://figma.com/community/file/{entry_id}" if figma_comm else None),
                video_url=(f"https://youtube.com/watch?v=sample{entry_id}" if video else None),
                likes=likes,
                comments=comments,
                engagement_score=likes + (comments * 2),
                winner=is_winner,
                winner_category=cat,
                creator_followers=followers,
                social_platforms_count=social_count,
                cross_posted_x=x,
                cross_posted_linkedin=li,
                cross_posted_instagram=ig,
                cross_posted_threads=th,
                cross_posted_bluesky=bs,
                in_contra_recap=in_recap,
                in_figma_blog=in_blog,
            )
            entries.append(entry)

    return entries


def main():
    print("Generating sample data for testing...")
    entries = generate_sample_entries()

    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    fieldnames = list(Entry.__dataclass_fields__.keys())
    with open(data_dir / "all_entries.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for entry in entries:
            writer.writerow(entry.to_dict())

    winners = [e for e in entries if e.winner]
    with open(data_dir / "winners.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for entry in winners:
            writer.writerow(entry.to_dict())

    print(f"Generated {len(entries)} total entries, {len(winners)} winners")
    print(f"Saved to data/all_entries.csv and data/winners.csv")


if __name__ == "__main__":
    main()
