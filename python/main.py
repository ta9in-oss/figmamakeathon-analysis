#!/usr/bin/env python3
"""Full pipeline — scrape, analyze, and generate the final report."""

import sys
import csv
from pathlib import Path

from src.config import EDITIONS
from src.models import Entry


def main():
    print("=" * 60)
    print("  FIGMA × CONTRA MAKEATHON ANALYSIS PIPELINE")
    print("=" * 60)

    # ── Phase 1 & 2: Scraping ───────────────────────────────────────────
    print("\n[Phase 1 & 2] Scraping Contra community pages...")
    print("  (This requires Playwright — install with: playwright install chromium)\n")

    all_entries: list[Entry] = []
    winners: list[Entry] = []

    from src.scraper import ContraScraper

    with ContraScraper(headless=True) as scraper:
        for edition in EDITIONS:
            print(f"\n  Edition: {edition.name}")
            print(f"  URL: {edition.topic_url}")

            try:
                entries = scraper.scrape_edition_topic(edition)
                print(f"  Scraped {len(entries)} entries")

                # Mark winners
                for entry in entries:
                    entry.winner = scraper._check_winner(
                        entry.project_title, entry.creator_name, edition
                    )
                    if entry.winner:
                        entry.winner_category = scraper._get_winner_category(
                            entry.project_title, entry.creator_name, edition
                        )
                        # Scrape winner details
                        entry = scraper.scrape_winner_details(entry, edition)
                        winners.append(entry)

                all_entries.extend(entries)
            except Exception as e:
                print(f"  ERROR scraping {edition.name}: {e}")
                continue

    # ── Save CSVs ───────────────────────────────────────────────────────
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    if all_entries:
        fieldnames = list(Entry.__dataclass_fields__.keys())
        with open(data_dir / "all_entries.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for entry in all_entries:
                writer.writerow(entry.to_dict())
        print(f"\n  Saved {len(all_entries)} entries to data/all_entries.csv")

    if winners:
        fieldnames = list(Entry.__dataclass_fields__.keys())
        with open(data_dir / "winners.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for entry in winners:
                writer.writerow(entry.to_dict())
        print(f"  Saved {len(winners)} winners to data/winners.csv")

    # ── Phase 3: Analysis ───────────────────────────────────────────────
    if all_entries:
        print("\n[Phase 3] Running analysis...")
        from src.analysis import load_data, compute_derived_fields, generate_all_charts, run_analysis

        df = load_data("data/all_entries.csv")
        df = compute_derived_fields(df)

        for edition in EDITIONS:
            result = run_analysis(df, edition.name)
            from src.analysis import print_summary
            print_summary(result)

        charts = generate_all_charts(df)
        print(f"\n  Generated {len(charts)} charts in output/figures/")

        # ── Report Generation ───────────────────────────────────────────
        print("\n[Report] Generating publishable article...")
        from src.report import generate_report, render_html, save_report

        report_md = generate_report(df)
        report_html = render_html(report_md)
        save_report(report_md, report_html)

    print("\n" + "=" * 60)
    print("  PIPELINE COMPLETE")
    print(f"  → data/all_entries.csv")
    print(f"  → data/winners.csv")
    print(f"  → output/figures/*.html (interactive charts)")
    print(f"  → output/report.md")
    print(f"  → output/index.html (web page)")
    print("=" * 60)


if __name__ == "__main__":
    main()
