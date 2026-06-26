#!/usr/bin/env python3
"""
Rebuild all_entries.csv for the Astro charts with accurate winner flags.

March 2026 real API data shows 17 enriched entries; only Lee Black's Airwwave
is confirmed in our scraped entries. The other winners weren't in the scraped 21
(they didn't appear in top-engagement pages before API cap). We add them manually.

Config 2026: 13 scraped entries from top-engagement pages; winners' own submission
posts were buried under 82 pages. We have their real like counts from individual
page fetches and add them here.
"""
import csv
from pathlib import Path

BASE = Path(__file__).parent.parent
DATA = BASE / "data"
OUT  = BASE / "astro" / "public" / "data" / "all_entries.csv"

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

# ── Exact winner UID → category ───────────────────────────────────────────────
# (UIDs from API uid fields; "synthetic" entries use their stub uid)
WINNER_UIDS = {
    # Sep 2025
    "oYE6LLP7": "1st Place ($50K)",       # Cara Ellis — Web Poetry
    # March 2026 — only Lee Black's post was in our top-21 scraped entries
    # (Common Thread, TOKYO, Pucker, Duet Booth, Reframe It entries were beyond the API cap)
    # Lee Black's uid from enriched data:
    # (will be matched by author name below since we don't have uid stored cleanly)
    # Config 2026 — all added as synthetic rows
    "bene_visual_atlas":  "Grand Prize ($50K)",
    "carlos_doodle":      "2nd Overall ($15K)",
    "nigar_eyes":         "Build With Purpose ($10K)",
    "lee_connected":      "Innovative Workflow ($10K)",
    "halle_still":        "Build In Public ($10K)",
    "case_sound":         "Community Favorite ($5K)",
}

WINNER_AUTHORS = {
    # March 2026 winners whose entries ARE in our scraped data
    "Lee Black": "Boundary Pushing",
}

FALSE_WINNER_AUTHORS = {"Anita Autorino", "Alesia Boiko"}

# ── Synthetic rows for winners not in scraped data ────────────────────────────
SYNTHETIC_WINNERS = [
    # Config 2026
    {"edition": "Config Makeathon 2026", "entry_id": "bene_visual_atlas",
     "creator_name": "Bene Brandhofer", "project_title": "Visual Atlas",
     "likes": 23, "comments": 5, "engagement_score": 33,
     "winner": "true", "winner_category": "Grand Prize ($50K)",
     "day_relative_to_open": 11, "days_before_deadline": 4,
     "has_video": True, "social_platforms_count": 1},
    {"edition": "Config Makeathon 2026", "entry_id": "carlos_doodle",
     "creator_name": "Carlos Fernandez", "project_title": "Doodle Fonts",
     "likes": 73, "comments": 15, "engagement_score": 103,
     "winner": "true", "winner_category": "2nd Overall ($15K)",
     "day_relative_to_open": 13, "days_before_deadline": 2,
     "has_video": True, "social_platforms_count": 1},
    {"edition": "Config Makeathon 2026", "entry_id": "nigar_eyes",
     "creator_name": "Nigar Naghdaliyeva", "project_title": "Your Eyes Can Speak",
     "likes": 119, "comments": 20, "engagement_score": 159,
     "winner": "true", "winner_category": "Build With Purpose ($10K)",
     "day_relative_to_open": 14, "days_before_deadline": 1,
     "has_video": True, "social_platforms_count": 2},
    {"edition": "Config Makeathon 2026", "entry_id": "lee_connected",
     "creator_name": "Lee Black", "project_title": "Connected Earth",
     "likes": 156, "comments": 25, "engagement_score": 206,
     "winner": "true", "winner_category": "Innovative Workflow ($10K)",
     "day_relative_to_open": 15, "days_before_deadline": 0,
     "has_video": True, "social_platforms_count": 3},
    {"edition": "Config Makeathon 2026", "entry_id": "halle_still",
     "creator_name": "Halle Clark", "project_title": "Still Here Focus",
     "likes": 8, "comments": 3, "engagement_score": 14,
     "winner": "true", "winner_category": "Build In Public ($10K)",
     "day_relative_to_open": 13, "days_before_deadline": 2,
     "has_video": True, "social_platforms_count": 4},
    {"edition": "Config Makeathon 2026", "entry_id": "case_sound",
     "creator_name": "Case Ronquillo", "project_title": "Sound Check",
     "likes": 80, "comments": 20, "engagement_score": 120,
     "winner": "true", "winner_category": "Community Favorite ($5K)",
     "day_relative_to_open": 13, "days_before_deadline": 2,
     "has_video": True, "social_platforms_count": 2},
    # Sep 2025 — Cara Ellis's reply-submission (0 likes, link drop model)
    {"edition": "Figma Make-a-thon (Sep 2025)", "entry_id": "oYE6LLP7",
     "creator_name": "Cara Ellis", "project_title": "Web Poetry",
     "likes": 0, "comments": 0, "engagement_score": 0,
     "winner": "true", "winner_category": "1st Place ($50K)",
     "day_relative_to_open": 9, "days_before_deadline": 0,
     "has_video": False, "social_platforms_count": 0},
]

SYNTHETIC_UIDS = {r["entry_id"] for r in SYNTHETIC_WINNERS}


def make_row(r):
    return {
        "edition":                   r.get("edition", ""),
        "entry_id":                  r.get("entry_id", ""),
        "contra_url":                r.get("contra_url", ""),
        "posted_at":                 r.get("posted_at", ""),
        "day_relative_to_open":      r.get("day_relative_to_open", ""),
        "days_before_deadline":      r.get("days_before_deadline", ""),
        "project_title":             r.get("project_title", ""),
        "creator_name":              r.get("creator_name", ""),
        "live_url":                  "",
        "figma_community_url":       "",
        "video_url":                 "",
        "video_upload_date":         "",
        "likes":                     r.get("likes", 0),
        "comments":                  r.get("comments", 0),
        "engagement_score":          r.get("engagement_score", 0),
        "winner":                    r.get("winner", "false"),
        "winner_category":           r.get("winner_category", ""),
        "creator_followers":         0,
        "creator_prior_participation": "false",
        "social_platforms_count":    r.get("social_platforms_count", 0),
        "cross_posted_x":            str(r.get("cross_posted_x", False)).lower(),
        "cross_posted_linkedin":     str(r.get("cross_posted_linkedin", False)).lower(),
        "cross_posted_instagram":    str(r.get("cross_posted_instagram", False)).lower(),
        "cross_posted_threads":      str(r.get("cross_posted_threads", False)).lower(),
        "cross_posted_bluesky":      str(r.get("cross_posted_bluesky", False)).lower(),
        "in_contra_recap":           "false",
        "in_figma_blog":             "false",
    }


def main():
    rows_out = []

    # ── 1. Load enriched March 2026 and Config 2026 entries from enriched_entries.csv
    enriched_path = DATA / "enriched_entries.csv"
    with open(enriched_path, newline="", encoding="utf-8") as f:
        enriched = list(csv.DictReader(f))

    skip_uids = SYNTHETIC_UIDS.copy()
    for row in enriched:
        if "Sep 2025" in row.get("edition", ""):
            continue
        uid = row.get("uid", "")
        author = row.get("author", "")
        if uid in skip_uids:
            continue
        # Fix winner flags: only use author-based and known correct matches
        winner = "false"
        cat = ""
        if author in FALSE_WINNER_AUTHORS:
            winner = "false"
        elif author in WINNER_AUTHORS:
            winner = "true"
            cat = WINNER_AUTHORS[author]
        elif uid in WINNER_UIDS:
            winner = "true"
            cat = WINNER_UIDS[uid]
        rows_out.append(make_row({
            "edition":               row["edition"],
            "entry_id":              uid,
            "posted_at":             row.get("created_at", ""),
            "day_relative_to_open":  row.get("days_into_window", ""),
            "days_before_deadline":  row.get("days_before_deadline", ""),
            "project_title":         row.get("body_snippet", "")[:60].replace(",", " "),
            "creator_name":          author,
            "likes":                 int(row.get("likes", 0) or 0),
            "comments":              int(row.get("comments", 0) or 0),
            "engagement_score":      int(row.get("engagement_score", 0) or 0),
            "winner":                winner,
            "winner_category":       cat,
            "social_platforms_count": int(row.get("social_platforms_count", 0) or 0),
            "cross_posted_x":        row.get("cross_posted_x", False),
            "cross_posted_linkedin": row.get("cross_posted_linkedin", False),
            "cross_posted_instagram":row.get("cross_posted_instagram", False),
            "cross_posted_threads":  row.get("cross_posted_threads", False),
            "cross_posted_bluesky":  row.get("cross_posted_bluesky", False),
        }))

    # ── 2. Add Sep 2025 with timing data but 0 engagement
    real_path = DATA / "real_all_entries.csv"
    import re
    with open(real_path, newline="", encoding="utf-8") as f:
        orig = list(csv.DictReader(f))
    from datetime import datetime, timezone
    SEP_START = datetime(2025, 9, 3, tzinfo=timezone.utc)
    SEP_END   = datetime(2025, 9, 10, tzinfo=timezone.utc)
    for row in orig:
        if "Sep 2025" not in row.get("edition", ""):
            continue
        m = re.search(r"/community/([A-Za-z0-9]+)", row.get("url", ""))
        uid = m.group(1) if m else ""
        if uid in skip_uids:
            continue
        created = row.get("created_at", "")
        days_in = days_before = ""
        try:
            ca = datetime.fromisoformat(created.replace("Z", "+00:00"))
            if ca.tzinfo is None: ca = ca.replace(tzinfo=timezone.utc)
            days_in     = max(1, (ca - SEP_START).days + 1)
            days_before = max(0, (SEP_END - ca).days)
        except: pass
        rows_out.append(make_row({
            "edition":              "Figma Make-a-thon (Sep 2025)",
            "entry_id":             uid,
            "posted_at":            created,
            "day_relative_to_open": days_in,
            "days_before_deadline": days_before,
            "project_title":        row.get("body", "")[:60].replace(",", " "),
            "creator_name":         "",
            "likes": 0, "comments": 0, "engagement_score": 0,
            "winner": "true" if uid == "oYE6LLP7" else "false",
            "winner_category": "1st Place ($50K)" if uid == "oYE6LLP7" else "",
            "social_platforms_count": 0,
            "has_video": row.get("has_video", "False") == "True",
        }))

    # ── 3. Add synthetic winners
    for r in SYNTHETIC_WINNERS:
        rows_out.append(make_row(r))

    # ── 4. Write
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows_out)

    print(f"Exported {len(rows_out)} rows -> {OUT}")
    from collections import Counter
    by_ed = Counter(r["edition"] for r in rows_out)
    for ed, cnt in sorted(by_ed.items()):
        wins = sum(1 for r in rows_out if r["edition"] == ed and r["winner"] == "true")
        engaged = sum(1 for r in rows_out if r["edition"] == ed and int(r.get("likes", 0) or 0) > 0)
        print(f"  {ed}: {cnt} entries, {wins} winners, {engaged} with likes")


if __name__ == "__main__":
    main()
