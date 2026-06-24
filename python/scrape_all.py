#!/usr/bin/env python3
"""Phase 2: Scrape all entries from Contra community topic pages."""

import csv
from pathlib import Path
from src.config import EDITIONS
from src.models import Entry
from src.scraper import ContraScraper


def main():
    print("Phase 2 — All Entries Scraping")
    all_entries: list[Entry] = []

    with ContraScraper(headless=True) as scraper:
        for edition in EDITIONS:
            print(f"\nEdition: {edition.name}")
            try:
                entries = scraper.scrape_edition_topic(edition)
                for entry in entries:
                    entry.winner = scraper._check_winner(
                        entry.project_title, entry.creator_name, edition
                    )
                    if entry.winner:
                        entry.winner_category = scraper._get_winner_category(
                            entry.project_title, entry.creator_name, edition
                        )
                all_entries.extend(entries)
                print(f"  Collected {len(entries)} entries")
            except Exception as e:
                print(f"  ERROR: {e}")

    Path("data").mkdir(exist_ok=True)
    fieldnames = list(Entry.__dataclass_fields__.keys())
    with open("data/all_entries.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for entry in all_entries:
            writer.writerow(entry.to_dict())

    print(f"\nSaved {len(all_entries)} total entries to data/all_entries.csv")


if __name__ == "__main__":
    main()
