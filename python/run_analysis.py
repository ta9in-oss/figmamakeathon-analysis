#!/usr/bin/env python3
"""
Run complete analysis on final_entries.csv and produce analysis_results.json
for use in the website.
"""
import csv, json, statistics
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

BASE = Path(__file__).parent.parent
DATA = BASE / "data"

# ── Known winner entries with real data ──────────────────────────────────────
# (uid, edition, author, project, place, likes, comments, created_at, days_into_window)
KNOWN_WINNER_ROWS = [
    # Sep 2025
    {"uid": "oYE6LLP7", "edition": "Figma Make-a-thon (Sep 2025)", "author": "Cara Ellis",
     "project": "Web Poetry", "place": "1st ($50K)", "likes": 0, "comments": 0,
     "created_at": "2025-09-11T07:09:40.943Z", "days_into_window": 9, "days_before_deadline": 0,
     "has_video": False, "social_platforms_count": 0},
    # March 2026 — Lee Black with Airwwave (222 likes from enriched data)
    {"uid": "airwwave_lee", "edition": "Figma Makeathon March 2026", "author": "Lee Black",
     "project": "Airwwave", "place": "Boundary Pushing", "likes": 222, "comments": 90,
     "created_at": "2026-02-15T00:00:00Z", "days_into_window": 14, "days_before_deadline": 29,
     "has_video": True, "social_platforms_count": 2},
    # Config 2026 winners
    {"uid": "bene_visual_atlas", "edition": "Config Makeathon 2026", "author": "Bene Brandhofer",
     "project": "Visual Atlas", "place": "Grand Prize ($50K)", "likes": 23, "comments": 5,
     "created_at": "2026-06-14T00:00:00Z", "days_into_window": 11, "days_before_deadline": 4,
     "has_video": True, "social_platforms_count": 1},
    {"uid": "carlos_doodle", "edition": "Config Makeathon 2026", "author": "Carlos Fernandez",
     "project": "Doodle Fonts", "place": "2nd Overall ($15K)", "likes": 73, "comments": 15,
     "created_at": "2026-06-16T00:00:00Z", "days_into_window": 13, "days_before_deadline": 2,
     "has_video": True, "social_platforms_count": 1},
    {"uid": "nigar_eyes", "edition": "Config Makeathon 2026", "author": "Nigar Naghdaliyeva",
     "project": "Your Eyes Can Speak", "place": "Build With Purpose ($10K)", "likes": 119, "comments": 20,
     "created_at": "2026-06-17T00:00:00Z", "days_into_window": 14, "days_before_deadline": 1,
     "has_video": True, "social_platforms_count": 2},
    {"uid": "lee_connected", "edition": "Config Makeathon 2026", "author": "Lee Black",
     "project": "Connected Earth", "place": "Innovative Workflow ($10K)", "likes": 156, "comments": 25,
     "created_at": "2026-06-18T00:00:00Z", "days_into_window": 15, "days_before_deadline": 0,
     "has_video": True, "social_platforms_count": 3},
    {"uid": "halle_still", "edition": "Config Makeathon 2026", "author": "Halle Clark",
     "project": "Still Here Focus", "place": "Build In Public ($10K)", "likes": 8, "comments": 3,
     "created_at": "2026-06-16T00:00:00Z", "days_into_window": 13, "days_before_deadline": 2,
     "has_video": True, "social_platforms_count": 4},
    {"uid": "case_sound", "edition": "Config Makeathon 2026", "author": "Case Ronquillo",
     "project": "Sound Check", "place": "Community Favorite ($5K)", "likes": 80, "comments": 20,
     "created_at": "2026-06-16T00:00:00Z", "days_into_window": 13, "days_before_deadline": 2,
     "has_video": True, "social_platforms_count": 2},
]

def safe_mean(vals):
    clean = [v for v in vals if v is not None]
    return round(statistics.mean(clean), 1) if clean else 0.0

def safe_median(vals):
    clean = [v for v in vals if v is not None]
    return round(statistics.median(clean), 1) if clean else 0.0

def pct(vals):
    if not vals: return 0.0
    return round(sum(1 for v in vals if v) / len(vals) * 100, 1)


def analyze_edition(rows, edition_name):
    winners     = [r for r in rows if str(r.get("is_winner", "")).lower() == "true"]
    non_winners = [r for r in rows if str(r.get("is_winner", "")).lower() != "true"]

    def get_int(r, k, default=0):
        v = r.get(k, default)
        try:
            return int(v)
        except (TypeError, ValueError):
            return default

    def get_float(r, k, default=None):
        v = r.get(k, default)
        if v is None or v == "":
            return None
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    def bool_val(r, k):
        v = r.get(k, False)
        if isinstance(v, bool):
            return v
        return str(v).lower() in ("true", "1", "yes")

    w_days   = [get_float(r, "days_into_window") for r in winners if get_float(r, "days_into_window") is not None]
    nw_days  = [get_float(r, "days_into_window") for r in non_winners if get_float(r, "days_into_window") is not None]
    w_eng    = [get_int(r, "engagement_score") for r in winners]
    nw_eng   = [get_int(r, "engagement_score") for r in non_winners]
    w_soc    = [get_int(r, "social_platforms_count") for r in winners]
    nw_soc   = [get_int(r, "social_platforms_count") for r in non_winners]
    w_vid    = [bool_val(r, "has_video") for r in winners]
    nw_vid   = [bool_val(r, "has_video") for r in non_winners]
    w_likes  = [get_int(r, "likes") for r in winners]
    nw_likes = [get_int(r, "likes") for r in non_winners]

    return {
        "edition": edition_name,
        "total_entries": len(rows),
        "total_winners": len(winners),
        "winner_avg_post_day": safe_mean(w_days),
        "non_winner_avg_post_day": safe_mean(nw_days),
        "winner_avg_engagement": safe_mean(w_eng),
        "non_winner_avg_engagement": safe_mean(nw_eng),
        "winner_avg_likes": safe_mean(w_likes),
        "non_winner_avg_likes": safe_mean(nw_likes),
        "winner_avg_social": safe_mean(w_soc),
        "non_winner_avg_social": safe_mean(nw_soc),
        "winner_video_pct": pct(w_vid),
        "non_winner_video_pct": pct(nw_vid),
        "winner_entries": [
            {"author": r.get("author", ""), "project": r.get("winner_category", ""),
             "likes": get_int(r, "likes"), "days": get_float(r, "days_into_window"),
             "social": get_int(r, "social_platforms_count"), "has_video": bool_val(r, "has_video")}
            for r in winners
        ],
    }


def main():
    # Load final_entries.csv
    final_path = DATA / "final_entries.csv"
    with open(final_path, newline="", encoding="utf-8") as f:
        all_rows = list(csv.DictReader(f))

    print(f"Loaded {len(all_rows)} rows from final_entries.csv")

    # Add known winner rows as explicit overrides
    known_uids = {r["uid"] for r in KNOWN_WINNER_ROWS}
    # Remove existing entries for these UIDs
    all_rows = [r for r in all_rows if r.get("uid") not in known_uids]

    # Add known winner rows
    for kw in KNOWN_WINNER_ROWS:
        all_rows.append({
            "edition":               kw["edition"],
            "id":                    kw.get("uid", ""),
            "uid":                   kw["uid"],
            "url":                   "",
            "author":                kw["author"],
            "username":              "",
            "created_at":            kw["created_at"],
            "days_into_window":      kw["days_into_window"],
            "days_before_deadline":  kw["days_before_deadline"],
            "likes":                 kw["likes"],
            "comments":              kw["comments"],
            "engagement_score":      kw["likes"] + kw["comments"] * 2,
            "has_video":             kw["has_video"],
            "video_count":           1 if kw["has_video"] else 0,
            "cross_posted_x":        False,
            "cross_posted_linkedin": False,
            "cross_posted_instagram":False,
            "cross_posted_threads":  False,
            "cross_posted_bluesky":  False,
            "social_platforms_count":kw["social_platforms_count"],
            "is_winner":             "True",
            "winner_category":       kw["place"],
            "is_reply":              False,
            "is_pinned":             False,
            "body_snippet":          f"{kw['project']} by {kw['author']}",
        })

    # Analyze per edition
    editions = ["Figma Make-a-thon (Sep 2025)", "Figma Makeathon March 2026", "Config Makeathon 2026"]
    results = {}
    for ed in editions:
        ed_rows = [r for r in all_rows if r.get("edition") == ed]
        results[ed] = analyze_edition(ed_rows, ed)
        r = results[ed]
        print(f"\n[{ed}]")
        print(f"  Entries: {r['total_entries']}, Winners: {r['total_winners']}")
        print(f"  Avg post day — winners: {r['winner_avg_post_day']}, non-winners: {r['non_winner_avg_post_day']}")
        print(f"  Avg engagement — winners: {r['winner_avg_engagement']}, non-winners: {r['non_winner_avg_engagement']}")
        print(f"  Avg likes — winners: {r['winner_avg_likes']}, non-winners: {r['non_winner_avg_likes']}")
        print(f"  Social platforms — winners: {r['winner_avg_social']}, non-winners: {r['non_winner_avg_social']}")
        print(f"  Has video — winners: {r['winner_video_pct']}%, non-winners: {r['non_winner_video_pct']}%")

    # Cross-edition summary
    all_winners     = [r for r in all_rows if str(r.get("is_winner", "")).lower() == "true"]
    all_non_winners = [r for r in all_rows if str(r.get("is_winner", "")).lower() != "true"]

    def get_int(r, k):
        try: return int(r.get(k, 0) or 0)
        except: return 0
    def get_float(r, k):
        try:
            v = r.get(k)
            return float(v) if v not in (None, "") else None
        except: return None
    def bool_val(r, k):
        v = r.get(k, False)
        return str(v).lower() in ("true", "1", "yes")

    summary = {
        "total_entries": len(all_rows),
        "total_winners": len(all_winners),
        "winner_avg_engagement": safe_mean([get_int(r, "engagement_score") for r in all_winners]),
        "non_winner_avg_engagement": safe_mean([get_int(r, "engagement_score") for r in all_non_winners]),
        "winner_avg_post_day": safe_mean([get_float(r, "days_into_window") for r in all_winners if get_float(r, "days_into_window") is not None]),
        "non_winner_avg_post_day": safe_mean([get_float(r, "days_into_window") for r in all_non_winners if get_float(r, "days_into_window") is not None]),
        "winner_avg_social": safe_mean([get_int(r, "social_platforms_count") for r in all_winners]),
        "non_winner_avg_social": safe_mean([get_int(r, "social_platforms_count") for r in all_non_winners]),
        "winner_video_pct": pct([bool_val(r, "has_video") for r in all_winners]),
        "non_winner_video_pct": pct([bool_val(r, "has_video") for r in all_non_winners]),
        "editions": results,
    }

    print(f"\n=== Cross-Edition Summary ===")
    print(f"Total: {summary['total_entries']} entries, {summary['total_winners']} winners")
    print(f"Winners avg engagement: {summary['winner_avg_engagement']} vs non-winners: {summary['non_winner_avg_engagement']}")
    print(f"Winners avg post day: {summary['winner_avg_post_day']} vs non-winners: {summary['non_winner_avg_post_day']}")
    print(f"Winners avg social: {summary['winner_avg_social']} vs non-winners: {summary['non_winner_avg_social']}")

    # Save
    out = DATA / "analysis_results.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved -> {out}")

    return summary


if __name__ == "__main__":
    main()
