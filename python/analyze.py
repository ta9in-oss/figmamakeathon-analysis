#!/usr/bin/env python3
"""Phase 3: Run analysis and generate charts from scraped data."""

import sys
from pathlib import Path
from src.analysis import (
    load_data,
    compute_derived_fields,
    run_analysis,
    generate_all_charts,
    print_summary,
)
from src.config import EDITIONS
from src.report import generate_report, render_html, save_report


def main():
    print("Phase 3 — Analysis & Report Generation")

    try:
        df = load_data("data/all_entries.csv")
    except FileNotFoundError:
        print("ERROR: data/all_entries.csv not found. Run scrape_all.py first.")
        sys.exit(1)

    df = compute_derived_fields(df)
    print(f"Loaded {len(df)} entries, {df['winner_bool'].sum()} winners")

    # Per-edition analysis
    for edition in EDITIONS:
        result = run_analysis(df, edition.name)
        print_summary(result)

    # All-editions aggregate
    result = run_analysis(df, None)
    print_summary(result)

    # Generate charts
    charts = generate_all_charts(df)
    print(f"\nGenerated {len(charts)} charts in output/figures/")

    # Generate report
    report_md = generate_report(df)
    report_html = render_html(report_md)
    save_report(report_md, report_html)


if __name__ == "__main__":
    main()
