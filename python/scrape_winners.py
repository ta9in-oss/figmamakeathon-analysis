#!/usr/bin/env python3
"""Phase 1: Scrape detailed metadata for all known winners."""

import csv
from pathlib import Path
from src.config import EDITIONS
from src.models import Entry
from src.scraper import ContraScraper


def main():
    print("Phase 1 — Winners Deep Dive")
    winners: list[Entry] = []

    with ContraScraper(headless=True) as scraper:
        for edition in EDITIONS:
            for seed in edition.winner_seed:
                if not seed.get("contra_url"):
                    print(f"  Skipping {seed.get('project')} — no Contra URL in seed data")
                    continue

                print(f"  Scraping: {seed.get('project')} by {seed.get('creator')}")
                entry = Entry(
                    edition=edition.name,
                    project_title=seed.get("project", ""),
                    creator_name=seed.get("creator", ""),
                    contra_url=seed.get("contra_url", ""),
                    winner=True,
                    winner_category=seed.get("place", ""),
                )
                entry = scraper.scrape_winner_details(entry, edition)
                winners.append(entry)

    Path("data").mkdir(exist_ok=True)
    fieldnames = list(Entry.__dataclass_fields__.keys())
    with open("data/winners.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for w in winners:
            writer.writerow(w.to_dict())

    print(f"\nSaved {len(winners)} winners to data/winners.csv")


if __name__ == "__main__":
    main()
