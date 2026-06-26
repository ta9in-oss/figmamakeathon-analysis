#!/usr/bin/env python3
"""
Export final_entries.csv to the chart-compatible all_entries.csv format
for the Astro website's chart components.
"""
import csv
from pathlib import Path

BASE = Path(__file__).parent.parent
SRC  = BASE / "data" / "final_entries.csv"
DST  = BASE / "astro" / "public" / "data" / "all_entries.csv"

# Schema expected by loadData.ts
FIELDS = [
    "edition", "entry_id", "contra_url", "posted_at",
    "day_relative_to_open", "days_before_deadline",
    "project_title", "creator_name",
    "live_url", "figma_community_url", "video_url", "video_upload_date",
    "likes", "comments", "engagement_score",
    "winner", "winner_category",
    "creator_followers", "creator_prior_participation", "social_platforms_count",
    "cross_posted_x", "cross_posted_linkedin", "cross_posted_instagram",
    "cross_posted_threads", "cross_posted_bluesky",
    "in_contra_recap", "in_figma_blog",
]

def bool_str(v):
    if isinstance(v, bool): return str(v).lower()
    if isinstance(v, str): return "true" if v.lower() in ("true","1","yes") else "false"
    return "false"

rows_out = []
with open(SRC, newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        is_w = row.get("is_winner", "false")
        winner_str = "true" if str(is_w).lower() in ("true","1","yes") else "false"
        rows_out.append({
            "edition":                   row.get("edition", ""),
            "entry_id":                  row.get("uid", ""),
            "contra_url":                row.get("url", ""),
            "posted_at":                 row.get("created_at", ""),
            "day_relative_to_open":      row.get("days_into_window", ""),
            "days_before_deadline":      row.get("days_before_deadline", ""),
            "project_title":             row.get("body_snippet", "")[:60].replace(",", " "),
            "creator_name":              row.get("author", ""),
            "live_url":                  "",
            "figma_community_url":       "",
            "video_url":                 "",
            "video_upload_date":         "",
            "likes":                     row.get("likes", 0),
            "comments":                  row.get("comments", 0),
            "engagement_score":          row.get("engagement_score", 0),
            "winner":                    winner_str,
            "winner_category":           row.get("winner_category", ""),
            "creator_followers":         0,
            "creator_prior_participation": "false",
            "social_platforms_count":    row.get("social_platforms_count", 0),
            "cross_posted_x":            bool_str(row.get("cross_posted_x", False)),
            "cross_posted_linkedin":     bool_str(row.get("cross_posted_linkedin", False)),
            "cross_posted_instagram":    bool_str(row.get("cross_posted_instagram", False)),
            "cross_posted_threads":      bool_str(row.get("cross_posted_threads", False)),
            "cross_posted_bluesky":      bool_str(row.get("cross_posted_bluesky", False)),
            "in_contra_recap":           "false",
            "in_figma_blog":             "false",
        })

with open(DST, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS)
    w.writeheader()
    w.writerows(rows_out)

print(f"Exported {len(rows_out)} rows -> {DST}")
print(f"  Winners: {sum(1 for r in rows_out if r['winner'] == 'true')}")
print(f"  With engagement: {sum(1 for r in rows_out if int(r['likes'] or 0) > 0)}")
